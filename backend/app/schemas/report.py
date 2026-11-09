from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class TurnReportItem(BaseModel):
    turn_index: int
    targeted_skill: str
    source_topic: str
    cited_concept: str
    question_text: str
    candidate_answer: Optional[str] = None
    score: Optional[float] = None
    technical_accuracy: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    missing_points: List[str] = Field(default_factory=list)
    constructive_feedback: Optional[str] = None
    model_answer_summary: Optional[str] = None
    retrieved_chunks_preview: List[Dict[str, Any]] = Field(default_factory=list)

class FinalReportResponse(BaseModel):
    session_id: str
    candidate_name: str
    target_role: str
    experience_level: str
    overall_score: float
    performance_tier: str  # Excellent, Proficient, Developing, Inadequate
    total_turns: int
    completed_turns: int
    status: str
    created_at: datetime
    summary: str
    strengths: List[str]
    areas_for_improvement: List[str]
    hiring_recommendation: str
    turns: List[TurnReportItem]
