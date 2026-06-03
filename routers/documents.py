from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from schemas import DocumentIngest, DocumentResponse, BulkIngestRequest, BulkIngestResponse
from services.embeddings import get_embedding, get_embeddings_batch

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/ingest", response_model=DocumentResponse, status_code=201)
async def ingest_document(doc: DocumentIngest, db: Session = Depends(get_db)):
    embedding = get_embedding(doc.content)  # no await

    new_doc = Document(
        title=doc.title,
        content=doc.content,
        category=doc.category,
        embedding=embedding
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


@router.post("/ingest/bulk", response_model=BulkIngestResponse, status_code=201)
async def bulk_ingest(request: BulkIngestRequest, db: Session = Depends(get_db)):
    texts = [doc.content for doc in request.documents]
    embeddings = get_embeddings_batch(texts)  # no await

    saved_docs = []
    for doc, embedding in zip(request.documents, embeddings):
        new_doc = Document(
            title=doc.title,
            content=doc.content,
            category=doc.category,
            embedding=embedding
        )
        db.add(new_doc)
        saved_docs.append(new_doc)

    db.commit()
    for doc in saved_docs:
        db.refresh(doc)

    return {"ingested": len(saved_docs), "documents": saved_docs}


@router.get("/", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()
