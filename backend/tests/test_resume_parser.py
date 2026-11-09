import pytest
from pathlib import Path
from app.services.resume_parser import resume_parser
from app.core.config import settings

SAMPLE_DIR = Path(settings.SAMPLE_RESUMES_DIR)

@pytest.mark.asyncio
async def test_parse_sample_text_resume():
    txt_path = SAMPLE_DIR / "resume_ai_ml_engineer.txt"
    assert txt_path.exists(), f"Missing sample resume at {txt_path}"
    content = txt_path.read_bytes()
    profile = await resume_parser.parse_resume(content, "resume_ai_ml_engineer.txt", "AI/ML Engineer")
    
    assert profile.candidate_name == "Sarah Chen"
    assert "PyTorch" in profile.skills or "Python" in profile.skills
    assert len(profile.domain_exposure) > 0
    assert profile.experience_level in ["Senior", "Lead / Staff", "Mid-Level"]

@pytest.mark.asyncio
async def test_parse_sample_pdf_resume():
    pdf_path = SAMPLE_DIR / "resume_backend_engineer.pdf"
    assert pdf_path.exists(), f"Missing sample PDF at {pdf_path}"
    content = pdf_path.read_bytes()
    profile = await resume_parser.parse_resume(content, "resume_backend_engineer.pdf", "Backend Engineer")
    
    assert "Marcus Vance" in profile.candidate_name
    assert any(s in profile.skills for s in ["FastAPI", "Go", "PostgreSQL", "Redis"])
    assert "Senior" in profile.experience_level or "Staff" in profile.experience_level

@pytest.mark.asyncio
async def test_parse_empty_resume_raises_error():
    with pytest.raises(ValueError):
        await resume_parser.parse_resume(b"", "empty.txt", "AI/ML Engineer")
