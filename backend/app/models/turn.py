import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class InterviewTurn(Base):
    __tablename__ = "interview_turns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    session_id = Column(String(36), ForeignKey("candidate_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    turn_index = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5
    
    # Question details
    targeted_skill = Column(String(100), nullable=False)
    source_topic = Column(String(200), nullable=False)
    question_text = Column(Text, nullable=False)
    cited_concept = Column(String(255), nullable=True)
    retrieved_chunks = Column(JSON, default=list)  # Ground-truth context chunks
    
    # Candidate Response & Evaluation
    candidate_answer = Column(Text, nullable=True)
    score = Column(Float, nullable=True)  # 1.0 to 10.0
    evaluation_feedback = Column(JSON, nullable=True)  # Accuracy, strengths, improvements, model answer
    
    created_at = Column(DateTime, default=utc_now)
    submitted_at = Column(DateTime, nullable=True)

    # Relationship
    session = relationship("CandidateSession", back_populates="turns")
