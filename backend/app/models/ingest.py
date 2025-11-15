from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class IngestRequest(BaseModel):
    """Request to ingest a new paper"""
    title: str = Field(..., min_length=1)
    pdf_url: Optional[HttpUrl] = None  # URL to download PDF
    pdf_path: Optional[str] = None  # Local file path
    authors: Optional[str] = None
    year: Optional[int] = None

class IngestResponse(BaseModel):
    """Response after ingestion"""
    status: str  # "success" or "failed"
    paper_id: str
    message: str
    chunks_indexed: int  # Number of text chunks added to FAISS