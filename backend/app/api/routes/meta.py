from pathlib import Path
from fastapi import APIRouter
from app.core.config import settings
from app.services.rag_engine import rag_engine

router = APIRouter(tags=["Metadata & Samples"])

@router.get("/roles")
def get_roles():
    """List available job screening roles."""
    return {
        "roles": [
            {
                "id": "AI/ML Engineer",
                "title": "AI/ML Engineer",
                "description": "Deep learning, RAG systems, model evaluation, loss functions & optimization",
                "corpus_source": "The Hundred-Page Machine Learning Book (Andriy Burkov)"
            },
            {
                "id": "Backend Engineer",
                "title": "Backend Engineer",
                "description": "Distributed architecture, async I/O, database indexing, caching & resiliency",
                "corpus_source": "Backend Systems & Distributed Architecture Handbook"
            },
            {
                "id": "Data Scientist",
                "title": "Data Scientist",
                "description": "Feature engineering, statistical modeling, ROC-AUC calibration, hypothesis testing",
                "corpus_source": "Machine Learning & Applied Statistics Handbook"
            }
        ]
    }

@router.get("/sample-resumes")
def get_sample_resumes():
    """List pre-loaded sample resumes for instant zero-friction testing."""
    return {
        "samples": [
            {
                "id": "resume_ai_ml_engineer",
                "name": "Sarah Chen",
                "role": "AI/ML Engineer",
                "experience_level": "Senior",
                "skills": ["PyTorch", "Transformers", "LangChain", "ChromaDB", "FastAPI"],
                "summary": "AI/ML Engineer with 4+ years architecting enterprise RAG pipelines and fine-tuning LLMs."
            },
            {
                "id": "resume_backend_engineer",
                "name": "Marcus Vance",
                "role": "Backend Engineer",
                "experience_level": "Senior / Staff",
                "skills": ["FastAPI", "Go", "PostgreSQL", "Redis", "Kafka", "Docker"],
                "summary": "Distributed systems architect with 5+ years building 45k req/sec transactional microservices."
            },
            {
                "id": "resume_data_scientist",
                "name": "Elena Rostova",
                "role": "Data Scientist",
                "experience_level": "Mid-Level",
                "skills": ["Python", "Scikit-Learn", "XGBoost", "Pandas", "SQL", "Statsmodels"],
                "summary": "Data Scientist with 3+ years applying statistical modeling and churn prediction with 0.88 ROC-AUC."
            }
        ]
    }

@router.get("/health")
def health_check():
    """System health check and diagnostic metrics."""
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "indexed_chunks_count": rag_engine.collection.count(),
        "database_url": settings.DATABASE_URL.split("///")[-1],
        "llm_provider": settings.LLM_PROVIDER
    }
