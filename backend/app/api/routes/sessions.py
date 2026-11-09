import os
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.session import CandidateSession
from app.models.turn import InterviewTurn
from app.schemas.candidate import ParsedCandidateProfile
from app.schemas.session import (
    SessionStartResponse,
    TurnQuestionResponse,
    AnswerSubmissionRequest,
    AnswerEvaluationResponse,
)
from app.schemas.report import FinalReportResponse, TurnReportItem
from app.services.resume_parser import resume_parser
from app.services.rag_engine import rag_engine
from app.services.question_gen import question_gen
from app.services.evaluator import evaluator

router = APIRouter(prefix="/sessions", tags=["Candidate Sessions"])

@router.post("/start", response_model=SessionStartResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    file: Optional[UploadFile] = File(None),
    role: str = Form(...),
    sample_resume_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handle resume upload (PDF / text) or sample resume selection + role selection.
    Extracts candidate profile, initializes CandidateSession, and persists in DB.
    """
    valid_roles = ["AI/ML Engineer", "Backend Engineer", "Data Scientist"]
    if role not in valid_roles:
        # Check case-insensitive match
        matched_role = next((r for r in valid_roles if r.lower() == role.lower()), None)
        if not matched_role:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid target role '{role}'. Allowed roles: {', '.join(valid_roles)}"
            )
        role = matched_role

    file_bytes = b""
    filename = "resume.txt"

    if sample_resume_id:
        sample_path_pdf = Path(settings.SAMPLE_RESUMES_DIR) / f"{sample_resume_id}.pdf"
        sample_path_txt = Path(settings.SAMPLE_RESUMES_DIR) / f"{sample_resume_id}.txt"
        if sample_path_pdf.exists():
            file_bytes = sample_path_pdf.read_bytes()
            filename = sample_path_pdf.name
        elif sample_path_txt.exists():
            file_bytes = sample_path_txt.read_bytes()
            filename = sample_path_txt.name
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sample resume '{sample_resume_id}' not found."
            )
    elif file:
        filename = file.filename or "resume.pdf"
        file_bytes = await file.read()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either an uploaded resume file or sample_resume_id must be provided."
        )

    try:
        profile: ParsedCandidateProfile = await resume_parser.parse_resume(
            file_bytes=file_bytes,
            filename=filename,
            target_role=role
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process resume: {str(e)}"
        )

    # Create new CandidateSession
    session_obj = CandidateSession(
        candidate_name=profile.candidate_name,
        email=profile.email,
        target_role=role,
        experience_level=profile.experience_level,
        parsed_skills=profile.skills,
        domain_exposure=profile.domain_exposure,
        project_highlights=profile.project_highlights,
        raw_summary=profile.raw_summary,
        total_turns=settings.QUESTIONS_PER_SESSION,
        current_turn_index=0,
        status="IN_PROGRESS"
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)

    return SessionStartResponse(
        session_id=session_obj.id,
        candidate_name=session_obj.candidate_name,
        target_role=session_obj.target_role,
        experience_level=session_obj.experience_level,
        parsed_skills=session_obj.parsed_skills,
        domain_exposure=session_obj.domain_exposure,
        project_highlights=session_obj.project_highlights,
        raw_summary=session_obj.raw_summary,
        total_turns=session_obj.total_turns,
        current_turn_index=session_obj.current_turn_index,
        status=session_obj.status
    )

@router.get("/{id}/next-question", response_model=TurnQuestionResponse)
async def get_next_question(id: str, db: Session = Depends(get_db)):
    """
    Generate or retrieve the current question for the candidate session.
    If already generated for the current turn, return it; otherwise generate with RAG grounding.
    """
    session_obj = db.query(CandidateSession).filter(CandidateSession.id == id).first()
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID '{id}' was not found."
        )

    if session_obj.status == "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This interview session is already completed. Access the /report endpoint for final insights."
        )

    next_turn_idx = session_obj.current_turn_index + 1
    if next_turn_idx > session_obj.total_turns:
        session_obj.status = "COMPLETED"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All interview turns have been completed."
        )

    # Check if a turn for this index was already generated
    existing_turn = db.query(InterviewTurn).filter(
        InterviewTurn.session_id == id,
        InterviewTurn.turn_index == next_turn_idx
    ).first()

    if existing_turn:
        preview_text = existing_turn.retrieved_chunks[0].get("text", "")[:200] + "..." if existing_turn.retrieved_chunks else None
        return TurnQuestionResponse(
            session_id=id,
            turn_index=existing_turn.turn_index,
            total_turns=session_obj.total_turns,
            question_text=existing_turn.question_text,
            targeted_skill=existing_turn.targeted_skill,
            source_topic=existing_turn.source_topic,
            cited_concept=existing_turn.cited_concept or "",
            retrieved_context_preview=preview_text,
            status=session_obj.status
        )

    # Generate new grounded question
    turn_data = await question_gen.generate_turn_question(
        candidate_name=session_obj.candidate_name,
        target_role=session_obj.target_role,
        parsed_skills=session_obj.parsed_skills or [],
        project_highlights=session_obj.project_highlights or [],
        experience_level=session_obj.experience_level,
        turn_index=next_turn_idx,
        previous_turns=session_obj.turns
    )

    new_turn = InterviewTurn(
        session_id=id,
        turn_index=next_turn_idx,
        targeted_skill=turn_data["targeted_skill"],
        source_topic=turn_data["source_topic"],
        cited_concept=turn_data["cited_concept"],
        question_text=turn_data["question_text"],
        retrieved_chunks=turn_data["retrieved_chunks"],
        candidate_answer=None,
        score=None,
        evaluation_feedback=None
    )
    db.add(new_turn)
    db.commit()
    db.refresh(new_turn)

    preview_text = new_turn.retrieved_chunks[0].get("text", "")[:200] + "..." if new_turn.retrieved_chunks else None
    return TurnQuestionResponse(
        session_id=id,
        turn_index=new_turn.turn_index,
        total_turns=session_obj.total_turns,
        question_text=new_turn.question_text,
        targeted_skill=new_turn.targeted_skill,
        source_topic=new_turn.source_topic,
        cited_concept=new_turn.cited_concept or "",
        retrieved_context_preview=preview_text,
        status=session_obj.status
    )

@router.post("/{id}/submit-answer", response_model=AnswerEvaluationResponse)
async def submit_answer(
    id: str,
    payload: AnswerSubmissionRequest,
    db: Session = Depends(get_db)
):
    """
    Accept candidate response, evaluate it against ground-truth textbook context,
    record score and detailed feedback, advance turn index, and check for completion.
    """
    session_obj = db.query(CandidateSession).filter(CandidateSession.id == id).first()
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID '{id}' was not found."
        )

    if session_obj.status == "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview session is already completed."
        )

    current_turn_idx = session_obj.current_turn_index + 1
    turn = db.query(InterviewTurn).filter(
        InterviewTurn.session_id == id,
        InterviewTurn.turn_index == current_turn_idx
    ).first()

    if not turn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No active question found for turn {current_turn_idx}. Fetch /next-question first."
        )

    # Evaluate candidate answer against ground truth
    eval_result = await evaluator.evaluate_answer(
        question_text=turn.question_text,
        targeted_skill=turn.targeted_skill,
        cited_concept=turn.cited_concept or "",
        retrieved_chunks=turn.retrieved_chunks or [],
        candidate_answer=payload.answer,
        experience_level=session_obj.experience_level
    )

    # Persist turn results
    turn.candidate_answer = payload.answer
    turn.score = eval_result["score"]
    turn.evaluation_feedback = eval_result
    turn.submitted_at = datetime.now(timezone.utc)

    # Advance session state
    session_obj.current_turn_index = current_turn_idx
    is_completed = current_turn_idx >= session_obj.total_turns

    if is_completed:
        session_obj.status = "COMPLETED"
        # Compute overall score
        all_turns = db.query(InterviewTurn).filter(InterviewTurn.session_id == id).all()
        scores = [t.score for t in all_turns if t.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        session_obj.overall_score = round(avg_score, 1)

    db.commit()

    return AnswerEvaluationResponse(
        session_id=id,
        turn_index=current_turn_idx,
        total_turns=session_obj.total_turns,
        score=eval_result["score"],
        technical_accuracy=eval_result.get("technical_accuracy", "Moderate"),
        strengths=eval_result.get("strengths", []),
        missing_points=eval_result.get("missing_points", []),
        constructive_feedback=eval_result.get("constructive_feedback", ""),
        model_answer_summary=eval_result.get("model_answer_summary", ""),
        is_completed=is_completed,
        next_turn_index=None if is_completed else current_turn_idx + 1
    )

@router.get("/{id}/report", response_model=FinalReportResponse)
async def get_session_report(id: str, db: Session = Depends(get_db)):
    """
    Return comprehensive interview performance summary, diagnostic breakdown,
    and ground-truth citations for all turns.
    """
    session_obj = db.query(CandidateSession).filter(CandidateSession.id == id).first()
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID '{id}' was not found."
        )

    all_turns = db.query(InterviewTurn).filter(InterviewTurn.session_id == id).order_by(InterviewTurn.turn_index).all()
    completed_turns_count = len([t for t in all_turns if t.candidate_answer is not None])

    # Calculate overall score
    scores = [t.score for t in all_turns if t.score is not None]
    overall_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    # Determine performance tier
    if overall_score >= 8.5:
        tier = "Staff / Principal Ready"
        rec = "Strong Hire: Demonstrates deep theoretical foundations and robust systems insight."
    elif overall_score >= 7.0:
        tier = "Senior Proficient"
        rec = "Hire: Solid technical knowledge with clear practical intuition."
    elif overall_score >= 5.5:
        tier = "Mid-Level Developing"
        rec = "Potential / Additional Screen: Competent in standard patterns but shows theoretical gaps."
    else:
        tier = "Needs Development"
        rec = "Do Not Advance: Significant foundational gaps regarding core concepts."

    # Aggregate strengths & improvements
    aggregated_strengths = []
    aggregated_improvements = []
    turn_items = []

    for t in all_turns:
        fb = t.evaluation_feedback or {}
        if fb.get("strengths"):
            aggregated_strengths.extend(fb.get("strengths"))
        if fb.get("missing_points"):
            aggregated_improvements.extend(fb.get("missing_points"))

        turn_items.append(TurnReportItem(
            turn_index=t.turn_index,
            targeted_skill=t.targeted_skill,
            source_topic=t.source_topic,
            cited_concept=t.cited_concept or "",
            question_text=t.question_text,
            candidate_answer=t.candidate_answer,
            score=t.score,
            technical_accuracy=fb.get("technical_accuracy"),
            strengths=fb.get("strengths", []),
            missing_points=fb.get("missing_points", []),
            constructive_feedback=fb.get("constructive_feedback"),
            model_answer_summary=fb.get("model_answer_summary"),
            retrieved_chunks_preview=t.retrieved_chunks or []
        ))

    # De-duplicate
    unique_strengths = list(dict.fromkeys(aggregated_strengths))[:6]
    unique_improvements = list(dict.fromkeys(aggregated_improvements))[:6]

    summary_text = (
        f"{session_obj.candidate_name} completed {completed_turns_count} of {session_obj.total_turns} technical evaluation turns "
        f"for the role of {session_obj.target_role} with an overall score of {overall_score}/10 ({tier})."
    )

    return FinalReportResponse(
        session_id=session_obj.id,
        candidate_name=session_obj.candidate_name,
        target_role=session_obj.target_role,
        experience_level=session_obj.experience_level,
        overall_score=overall_score,
        performance_tier=tier,
        total_turns=session_obj.total_turns,
        completed_turns=completed_turns_count,
        status=session_obj.status,
        created_at=session_obj.created_at,
        summary=summary_text,
        strengths=unique_strengths if unique_strengths else ["Completed technical screening"],
        areas_for_improvement=unique_improvements if unique_improvements else ["Review foundational textbook chapters"],
        hiring_recommendation=rec,
        turns=turn_items
    )
