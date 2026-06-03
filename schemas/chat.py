from pydantic import BaseModel
from typing import Optional


class SupportRequest(BaseModel):
    question: str
    category: Optional[str] = None  # optionally filter by category


class SourceDocument(BaseModel):
    title: str
    category: Optional[str] = None
    relevance_score: float


class SupportResponse(BaseModel):
    answer: str
    sources: list[SourceDocument]
    confidence: str  # "high", "medium", "low"
