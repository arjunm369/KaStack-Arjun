from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Education(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None


class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None


class Candidate(BaseModel):
    candidate_id: str
    education: List[Education] = []
    experience: List[Experience] = []
    skills: List[str] = []
    hobbies: List[str] = []
    certifications: List[str] = []
    projects: List[Dict[str, Any]] = []
    introduction: str = ""


class CandidateSummary(BaseModel):
    candidate_id: str
    introduction: str = ""
    skills: List[str] = []
    experience_count: int = 0
    education_count: int = 0


class QuestionRequest(BaseModel):
    question: str = Field(..., description="Natural language question about the candidate")





