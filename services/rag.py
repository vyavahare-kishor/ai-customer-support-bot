from sqlalchemy.orm import Session
from services.retrieval import find_similar_documents
from groq import Groq
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful customer support assistant.
Answer questions using ONLY the context provided below.
If the answer is not in the context, say "I don't have information about that — please contact our support team."
Be concise, friendly, and accurate.
Never make up information."""


async def answer_question(
    question: str,
    db: Session,
    category: str = None
) -> dict:
    """
    Full RAG pipeline:
    1. Find relevant documents via similarity search
    2. Build context from retrieved docs
    3. Generate answer using LLM
    4. Return answer + sources
    """

    # Step 1: Retrieve relevant documents
    docs_with_scores = await find_similar_documents(
        question=question,
        db=db,
        category=category,
        limit=3
    )

    if not docs_with_scores:
        return {
            "answer": "I don't have enough information to answer that. Please contact our support team.",
            "sources": [],
            "confidence": "low"
        }

    # Step 2: Build context from retrieved docs
    context_parts = []
    for doc, score in docs_with_scores:
        context_parts.append(f"[{doc.title}]\n{doc.content}")

    context = "\n\n---\n\n".join(context_parts)

    # Step 3: Generate answer with context injected
    prompt = f"""Context from knowledge base:
{context}

Customer question: {question}

Answer the question using only the context above."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512
    )

    answer = response.choices[0].message.content

    # Step 4: Determine confidence from top similarity score
    top_score = docs_with_scores[0][1]
    if top_score > 0.8:
        confidence = "high"
    elif top_score > 0.6:
        confidence = "medium"
    else:
        confidence = "low"

    # Step 5: Build source list
    sources = [
        {
            "title": doc.title,
            "category": doc.category,
            "relevance_score": round(score, 3)
        }
        for doc, score in docs_with_scores
    ]

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence
    }
