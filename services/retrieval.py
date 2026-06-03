from sqlalchemy.orm import Session
from sqlalchemy import text
from models import Document
from services.embeddings import get_embedding


async def find_similar_documents(
    question: str,
    db: Session,
    category: str = None,
    limit: int = 3
) -> list[tuple[Document, float]]:

    question_embedding = get_embedding(question)
    embedding_str = str(question_embedding)

    if category:
        query = text("""
            SELECT id, 1 - (embedding <=> CAST(:embedding AS vector)) AS score
            FROM documents
            WHERE category = :category
            AND embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)
        results = db.execute(query, {
            "embedding": embedding_str,
            "category": category,
            "limit": limit
        }).fetchall()
    else:
        query = text("""
            SELECT id, 1 - (embedding <=> CAST(:embedding AS vector)) AS score
            FROM documents
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)
        results = db.execute(query, {
            "embedding": embedding_str,
            "limit": limit
        }).fetchall()

    docs_with_scores = []
    for row in results:
        doc = db.query(Document).filter(Document.id == row.id).first()
        if doc:
            docs_with_scores.append((doc, float(row.score)))

    return docs_with_scores
