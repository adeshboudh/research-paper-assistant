from fastapi import APIRouter, HTTPException
from ..models.query import GraphRagRequest, GraphRagResponse, GraphNode, SourceInfo
from ..services.vector_service import vector_service
from ..services.graph_service import graph_service
from ..services.llm_service import llm_service
import logging

router = APIRouter(tags=["GraphRAG"])
logger = logging.getLogger(__name__)

@router.post("/query/graph", response_model=GraphRagResponse)
async def graph_rag_query(request: GraphRagRequest):
    """
    Hybrid retrieval: Neo4j graph query + FAISS vector search.

    Flow:
    1. Parse query for entities (paper titles, authors, concepts)
    2. Execute Cypher query on Neo4j (e.g., find citations)
    3. Run FAISS semantic search in parallel
    4. Merge graph results + text chunks
    5. Send combined context to LLM
    6. Return answer with graph nodes used
    """

    if not request.question or len(request.question) < 3:
        raise HTTPException(status_code=400, detail="Question is required.")

    # Step 1: FAISS Vector Search (same as RAG)
    vector_results = vector_service.search(request.question, top_k=request.top_k)

    # Step 2: Neo4j Graph Search
    graph_nodes = []

    if request.use_graph:
        # Extract keywords from question for graph search
        keywords = _extract_keywords(request.question)

        for keyword in keywords:
            # Search papers by keyword
            papers = graph_service.search_papers_by_keyword(keyword, limit=3)
            for paper in papers:
                graph_nodes.append({
                    'node_type': 'Paper',
                    'properties': paper
                })

            # Search by topic/concept
            topic_papers = graph_service.get_papers_by_topic(keyword, limit=2)
            for paper in topic_papers:
                graph_nodes.append({
                    'node_type': 'Paper',
                    'properties': paper
                })

            # Deduplicate graph nodes by paper ID
            seen_ids = set()
            unique_nodes = []
            for node in graph_nodes:
                node_id = node['properties'].get('id')
                if node_id and node_id not in seen_ids:
                    seen_ids.add(node_id)
                    unique_nodes.append(node)

            graph_nodes = unique_nodes[:5]  # Limit to top 5 graph nodes

            logger.info(f"Found {len(graph_nodes)} relevant graph nodes")

    # Step 3: Build response sources
    sources = [
        SourceInfo(
            paper_id=r.get("paper_id", "unknown"),
            title=r.get("title", "Research Paper"),
            snippet=r.get("text", "")[:200] + "...",
            page=r.get("page"),
            relevance_score=round(r.get("relevance_score", 0.0), 3)
        ) for r in vector_results
    ]

    # Step 4: Build graph node responses
    graph_node_responses = [
        GraphNode(
            node_type=node['node_type'],
            properties=node['properties']
        ) for node in graph_nodes
    ]

    # Step 5: Generate answer with LLM using hybrid context
    if not vector_results and not graph_nodes:
        answer = "Sorry, no relevant information was found in either the text corpus or knowledge graph for your question."
    else:
        answer = llm_service.generate_graph_rag_answer(
            request.question,
            vector_results,
            graph_nodes
        )

    return GraphRagResponse(
        answer=answer,
        sources=sources,
        graph_nodes=graph_node_responses,
        session_id=request.session_id or "N/A"
    )

def _extract_keywords(question: str) -> list:
    """
    Extract potential keywords from question for graph search.
    Simple implementation - can be enhanced with NER or keyword extraction.
    """
    # Remove common words
    stop_words = {
        'what', 'is', 'are', 'how', 'does', 'do', 'the', 'a', 'an', 'and',
        'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'about', 'tell', 'me', 'explain', 'describe', 'can', 'you', 'please'
    }

    # Extract words, convert to lowercase, remove punctuation
    words = question.lower().replace('?', '').replace(',', '').split()
    keywords = [w for w in words if w not in stop_words and len(w) > 3]

    # Return top 3 keywords
    return keywords[:3]