from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime


class DocumentIngest(BaseModel):
    title: str
    content: str
    category: Optional[str] = None


class DocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BulkIngestRequest(BaseModel):
    documents: list[DocumentIngest]


class BulkIngestResponse(BaseModel):
    ingested: int
    documents: list[DocumentResponse]
