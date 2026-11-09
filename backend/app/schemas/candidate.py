from typing import List, Optional
from pydantic import BaseModel, Field

class ParsedCandidateProfile(BaseModel):
    candidate_name: str = Field(default="Candidate", description="Full name of candidate")
    email: Optional[str] = Field(default=None, description="Contact email")
    skills: List[str] = Field(default_factory=list, description="Primary technical skills")
    technologies: List[str] = Field(default_factory=list, description="Libraries, frameworks, and tooling")
    experience_level: str = Field(default="Mid-Level", description="Junior, Mid-Level, Senior, or Lead")
    domain_exposure: List[str] = Field(default_factory=list, description="Key domain concepts")
    project_highlights: List[str] = Field(default_factory=list, description="Extracted key accomplishments/projects")
    raw_summary: Optional[str] = Field(default="", description="Executive summary of candidate profile")
