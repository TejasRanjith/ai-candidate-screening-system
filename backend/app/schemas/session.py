from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class SessionStartResponse(BaseModel):
    session_id: str
    candidate_name: str
    target_role: str
    experience_level: str
    parsed_skills: List[str]
    domain_exposure: List[str]
    project_highlights: List[str]
    raw_summary: Optional[str] = None
    total_turns: int = 5
    current_turn_index: int = 0
    status: str

class TurnQuestionResponse(BaseModel):
    session_id: str
    turn_index: int
    total_turns: int
    question_text: str
    targeted_skill: str
    source_topic: str
    cited_concept: str
    retrieved_context_preview: Optional[str] = None
    status: str

class AnswerSubmissionRequest(BaseModel):
    answer: str = Field(..., min_length=2, description="Candidate answer text or code")

class AnswerEvaluationResponse(BaseModel):
    session_id: str
    turn_index: int
    total_turns: int
    score: float
    technical_accuracy: str
    strengths: List[str]
    missing_points: List[str]
    constructive_feedback: str
    model_answer_summary: str
    is_completed: bool
    next_turn_index: Optional[int] = None
