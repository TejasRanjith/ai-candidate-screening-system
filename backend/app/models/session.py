import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class CandidateSession(Base):
    __tablename__ = "candidate_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    candidate_name = Column(String(255), nullable=False, default="Candidate")
    email = Column(String(255), nullable=True)
    target_role = Column(String(100), nullable=False)
    experience_level = Column(String(50), default="Mid-Level")
    
    # Parsed Profile details (JSON)
    parsed_skills = Column(JSON, default=list)
    domain_exposure = Column(JSON, default=list)
    project_highlights = Column(JSON, default=list)
    raw_summary = Column(Text, nullable=True)
    
    # Interview State Tracking
    total_turns = Column(Integer, default=5)
    current_turn_index = Column(Integer, default=0)
    status = Column(String(50), default="IN_PROGRESS")  # IN_PROGRESS, COMPLETED
    overall_score = Column(Float, default=0.0)
    final_report = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    turns = relationship("InterviewTurn", back_populates="session", cascade="all, delete-orphan", order_by="InterviewTurn.turn_index")
