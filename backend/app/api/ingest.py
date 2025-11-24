from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import os
import uuid
import logging
from ..models.ingest import IngestRequest, IngestResponse
from ..services.ingestion_service import ingestion_service
import httpx

router = APIRouter(tags=["Ingestion"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = "/data/papers"


@router.post("/ingest", response_model=IngestResponse)
async def ingest_paper(request: IngestRequest):
    """
    Ingest a paper from URL or local path

    Args:
        request: IngestRequest with paper metadata and PDF location

    Returns:
        IngestResponse with processing statistics
    """
    paper_id = str(uuid.uuid4())

    try:
        # Determine PDF source
        if request.pdf_url:
            # Download from URL
            pdf_url_str = str(request.pdf_url)
            logger.info(f"Downloading PDF from: {pdf_url_str}")
            pdf_path = await download_pdf(pdf_url_str, paper_id)
        elif request.pdf_path:
            # Use local file
            pdf_path = request.pdf_path
            if not os.path.exists(pdf_path):
                raise HTTPException(status_code=404, detail=f"PDF not found: {pdf_path}")
        else:
            raise HTTPException(status_code=400, detail="Either pdf_url or pdf_path must be provided")

        # Process the paper
        stats = ingestion_service.process_paper(
            pdf_path=pdf_path,
            paper_id=paper_id,
            title=request.title,
            authors=request.authors,
            year=request.year,
            abstract=None
        )

        return IngestResponse(
            status="success",
            paper_id=paper_id,
            message=f"Paper '{request.title}' ingested successfully",
            chunks_indexed=stats['chunks_created']
        )

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return IngestResponse(
            status="failed",
            paper_id=paper_id,
            message=f"Ingestion failed: {str(e)}",
            chunks_indexed=0
        )


@router.post("/ingest/upload", response_model=IngestResponse)
async def upload_and_ingest_paper(
        file: UploadFile = File(...),
        title: str = Form(...),
        authors: Optional[str] = Form(None),
        year: Optional[int] = Form(None)
):
    """
    Upload a PDF file and ingest it

    Args:
        file: PDF file upload
        title: Paper title
        authors: Author names
        year: Publication year

    Returns:
        IngestResponse with processing statistics
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    paper_id = str(uuid.uuid4())

    try:
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, f"{paper_id}.pdf")

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Saved uploaded PDF: {file_path}")

        # Process the paper
        stats = ingestion_service.process_paper(
            pdf_path=file_path,
            paper_id=paper_id,
            title=title,
            authors=authors,
            year=year
        )

        return IngestResponse(
            status="success",
            paper_id=paper_id,
            message=f"Paper '{title}' uploaded and ingested successfully",
            chunks_indexed=stats['chunks_created']
        )

    except Exception as e:
        logger.error(f"Upload/ingestion failed: {e}")
        return IngestResponse(
            status="failed",
            paper_id=paper_id,
            message=f"Upload/ingestion failed: {str(e)}",
            chunks_indexed=0
        )


async def download_pdf(url: str, paper_id: str) -> str:
    """
    Download PDF from URL

    Args:
        url: PDF URL
        paper_id: Unique paper ID

    Returns:
        Local file path
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{paper_id}.pdf")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

    logger.info(f"Downloaded PDF to: {file_path}")
    return file_path


@router.get("/ingest/stats")
async def get_ingestion_stats():
    """Get statistics about ingested papers"""
    from ..services.vector_service import vector_service
    from ..services.graph_service import graph_service

    return {
        "vector_store": vector_service.get_stats(),
        "knowledge_graph": graph_service.get_graph_stats()
    }
