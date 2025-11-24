from fastapi import APIRouter
from ..services.vector_service import vector_service
from ..services.graph_service import graph_service

router = APIRouter(tags=["Testing"])


@router.post("/test/add-sample-data")
async def add_sample_data():
    """Add sample research papers to test RAG functionality"""

    # Sample research paper chunks
    sample_texts = [
        "GraphRAG is a retrieval-augmented generation approach that combines knowledge graphs with vector embeddings. Unlike traditional RAG which only uses semantic search, GraphRAG leverages structured relationships between entities like papers, authors, and concepts to provide more comprehensive answers.",

        "The Transformer architecture introduced in 'Attention is All You Need' by Vaswani et al. (2017) revolutionized natural language processing. It uses self-attention mechanisms to process sequences in parallel, replacing recurrent neural networks. This architecture enabled models like BERT, GPT, and T5.",

        "FAISS (Facebook AI Similarity Search) is a library for efficient similarity search of dense vectors. It supports exact search with IndexFlatL2 and approximate search with IVF and HNSW indexes for billion-scale datasets. FAISS is commonly used in retrieval-augmented generation systems.",

        "Neo4j is a graph database that uses the Cypher query language. It's optimized for storing and querying connected data with nodes and relationships. Neo4j is ideal for knowledge graphs, recommendation systems, fraud detection, and network analysis applications.",

        "Retrieval-Augmented Generation (RAG) improves language model outputs by retrieving relevant context from external knowledge bases before generation. This approach grounds responses in factual data and significantly reduces hallucinations compared to pure language model generation.",

        "Sentence-transformers is a Python framework for state-of-the-art sentence, text, and image embeddings. It provides pre-trained models like all-MiniLM-L6-v2 that can encode text into 384-dimensional vectors for semantic similarity search.",

        "Knowledge graphs represent information as entities (nodes) and relationships (edges). They enable complex queries that traverse connections, such as finding all papers cited by an author or discovering research topics related to a concept.",

        "Vector databases store high-dimensional embeddings and enable fast similarity search. Popular options include FAISS, Pinecone, Weaviate, and Milvus. They are essential infrastructure for semantic search and RAG applications."
    ]

    # Metadata for each chunk
    paper_ids = [
        "paper_graphrag_2024",
        "paper_transformer_2017",
        "paper_faiss_2019",
        "paper_neo4j_2023",
        "paper_rag_2023",
        "paper_sentence_transformers_2021",
        "paper_knowledge_graphs_2022",
        "paper_vector_databases_2024"
    ]

    chunk_ids = [0, 0, 0, 0, 0, 0, 0, 0]

    # Add to FAISS
    vector_service.add_documents(sample_texts, paper_ids, chunk_ids)

    # Persist to disk
    vector_service.persist()

    stats = vector_service.get_stats()

    return {
        "status": "success",
        "message": "Sample data added to FAISS index",
        "chunks_added": len(sample_texts),
        "stats": stats
    }


@router.post("/test/add-sample-graph-data")
async def add_sample_graph_data():
    """Add sample papers and relationships to Neo4j"""

    # Add sample papers to Neo4j
    sample_papers = [
        {
            "id": "paper_graphrag_2024",
            "title": "GraphRAG: Combining Knowledge Graphs with Vector Search",
            "authors": "Smith, J., Chen, L.",
            "year": 2024,
            "abstract": "We introduce GraphRAG, a novel approach combining knowledge graphs with retrieval-augmented generation."
        },
        {
            "id": "paper_transformer_2017",
            "title": "Attention is All You Need",
            "authors": "Vaswani, A., et al.",
            "year": 2017,
            "abstract": "We propose the Transformer, a novel architecture based solely on attention mechanisms."
        },
        {
            "id": "paper_rag_2023",
            "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP",
            "authors": "Lewis, P., et al.",
            "year": 2023,
            "abstract": "RAG models combine pre-trained parametric and non-parametric memory for language generation."
        }
    ]

    for paper in sample_papers:
        graph_service.add_paper(paper)

    graph_stats = graph_service.get_graph_stats()

    return {
        "status": "success",
        "message": "Sample graph data added to Neo4j",
        "papers_added": len(sample_papers),
        "graph_stats": graph_stats
    }


@router.delete("/test/clear-all-data")
async def clear_all_data():
    """Clear all test data (use with caution!)"""

    # Clear FAISS index
    vector_service.index = None
    vector_service.metadata = []
    vector_service.initialize_index()
    vector_service.persist()

    return {
        "status": "success",
        "message": "All test data cleared"
    }


@router.post("/test/ingest-sample-pdf")
async def ingest_sample_pdf():
    """
    Download and ingest a sample PDF from arXiv for testing
    """
    from ..api.ingest import ingest_paper
    from ..models.ingest import IngestRequest

    # Sample paper: BERT paper
    request = IngestRequest(
        title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        pdf_url="https://arxiv.org/pdf/1810.04805.pdf",
        authors="Devlin, J., Chang, M.W., Lee, K., Toutanova, K.",
        year=2018
    )

    result = await ingest_paper(request)
    return result
