import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple
import logging
from ..core.config import settings
from .vector_service import vector_service
from .graph_service import graph_service

logger = logging.getLogger(__name__)

class IngestionService:
    """Service for ingesting research papers into the system"""

    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE  # words per chunk
        self.chunk_overlap = settings.CHUNK_OVERLAP  # words overlap

    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, Dict]:
        """
        Extract text and metadata from PDF using PyMuPDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (full_text, metadata_dict)
        """
        try:
            doc = fitz.open(pdf_path)

            # Extract text from all pages
            full_text = ""
            for page_num, page in enumerate(doc):
                text = page.get_text()
                full_text += f"\n[Page {page_num + 1}]\n{text}"

            # Extract metadata
            metadata = {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'page_count': len(doc)
            }

            doc.close()

            logger.info(f"Extracted {len(full_text)} characters from PDF ({metadata['page_count']} pages)")
            return full_text, metadata
        except Exception as e:
            logger.error(f"Failed to extract PDF: {e}")
            raise

    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks

        Args:
            text: Full document text

        Returns:
            List of chunks with metadata
        """
        # Clean text: remove/escape problematic characters
        text = text.replace('\x00', '')  # Remove null bytes

        # Split by paragraphs first (double newline) - using string split, not regex
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = []
        current_word_count = 0
        chunk_id = 0
        current_page = 1

        for para in paragraphs:
            # Track page numbers - use string operations instead of regex
            if '[Page ' in para:
                try:
                    # Extract page number safely
                    start = para.find('[Page ') + 6
                    end = para.find(']', start)
                    if end > start:
                        page_str = para[start:end].strip()
                        if page_str.isdigit():
                            current_page = int(page_str)
                        # Remove page marker from text
                        para = para[:para.find('[Page ')] + para[end + 1:]
                except (ValueError, IndexError):
                    pass  # Skip if page parsing fails

            para = para.strip()

            if not para or len(para) < 20:  # Skip very short paragraphs
                continue

            words = para.split()
            word_count = len(words)

            # If adding this paragraph exceeds chunk size, save current chunk
            if current_word_count + word_count > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': chunk_text,
                    'word_count': current_word_count,
                    'page': current_page
                })

                # Start new chunk with overlap
                overlap_words = current_chunk[-self.chunk_overlap:] if len(
                    current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_words + words
                current_word_count = len(current_chunk)
                chunk_id += 1
            else:
                current_chunk.extend(words)
                current_word_count += word_count

        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'word_count': current_word_count,
                'page': current_page
            })

        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks

    def process_paper(self, pdf_path: str, paper_id: str, title: str = None, authors: str = None, year: int = None, abstract: str = None) -> Dict:
        """
        Complete pipeline: extract, chunk, embed, and index a paper

        Args:
            pdf_path: Path to PDF file
            paper_id: Unique paper identifier
            title: Paper title (optional, extracted from PDF if not provided)
            authors: Author names (optional)
            year: Publication year (optional)
            abstract: Paper abstract (optional)

        Returns:
            Dict with processing statistics
        """
        logger.info(f"Processing paper: {paper_id}")

        # Step 1: Extract text from PDF
        full_text, pdf_metadata = self.extract_text_from_pdf(pdf_path)

        # Use provided metadata or fall back to PDF metadata
        final_title = title or pdf_metadata.get('title') or f"Paper {paper_id}"
        final_authors = authors or pdf_metadata.get('author') or "Unknown"

        # Step 2: Chunk the text
        chunks = self.chunk_text(full_text)

        if not chunks:
            raise ValueError("No valid chunks created from PDF")

        # Step 3: Add chunks to FAISS
        texts = [chunk['text'] for chunk in chunks]
        paper_ids = [paper_id] * len(chunks)
        chunk_ids = [chunk['chunk_id'] for chunk in chunks]

        vector_service.add_documents(texts, paper_ids, chunk_ids)

        # Step 4: Add paper to Neo4j knowledge graph
        graph_paper_data = {
            'id': paper_id,
            'title': final_title,
            'authors': final_authors,
            'year': year or 0,
            'abstract': abstract or full_text[:500]  # Use first 500 chars if no abstract
        }
        graph_service.add_paper(graph_paper_data)

        # Step 5: Persist FAISS index
        vector_service.persist()

        stats = {
            'paper_id': paper_id,
            'title': final_title,
            'chunks_created': len(chunks),
            'total_words': sum(c['word_count'] for c in chunks),
            'pages': pdf_metadata.get('page_count', 0)
        }

        logger.info(f"Paper processed: {stats}")
        return stats

# Global instance
ingestion_service = IngestionService()