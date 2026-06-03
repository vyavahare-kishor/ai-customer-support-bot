from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import SupportRequest, SupportResponse
from services.rag import answer_question

router = APIRouter(prefix="/support", tags=["Support"])


@router.post("/ask", response_model=SupportResponse)
async def ask_support(request: SupportRequest, db: Session = Depends(get_db)):
    """
    RAG-powered customer support endpoint.
    Ask any question — get answer from your knowledge base.
    """
    result = await answer_question(
        question=request.question,
        db=db,
        category=request.category
    )
    return result
