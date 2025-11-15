from fastapi import APIRouter, HTTPException, UploadFile, File
from ..models.ingest import IngestRequest, IngestResponse
import uuid

router = APIRouter(tags=["Ingestion"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_paper(request: IngestRequest):
    """
    Ingest a new research paper.

    Flow:
    1. Download/load PDF (PyMuPDF or GROBID)
    2. Extract text and metadata (title, authors, abstract)
    3. Chunk text into paragraphs/sections
    4. Generate embeddings for each chunk
    5. Add embeddings to FAISS index
    6. Create Neo4j nodes (Paper, Author, Concept) and relationships
    7. Persist FAISS index to disk
    """
    # TODO: Implement PDF parsing + indexing
    paper_id = str(uuid.uuid4())

    return IngestResponse(
        status="success",
        paper_id=paper_id,
        message=f"Paper '{request.title}' queued for ingestion",
        chunks_indexed=0
    )


@router.post("/ingest/upload")
async def upload_paper(file: UploadFile = File(...)):
    """Upload PDF directly for ingestion"""
    # TODO: Save file and trigger ingestion pipeline
    return {"filename": file.filename, "status": "uploaded"}
