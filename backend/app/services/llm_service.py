import google.generativeai as genai
from typing import List, Optional, Dict
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for generating answers using Google Gemini API"""

    def __init__(self):
        self.model = None
        self.configured = False

    def configure(self):
        """Configure Gemini API"""
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set")
            return

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.configured = True
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise

    def _build_rag_prompt(self, question: str, context_chunks: List[dict]) -> str:
        """
        Build prompt for standard RAG
        
        Args:
            question: User's question
            context_chunks: List of dicts with {text, paper_id, ...}
            
        Returns:
            Formatted prompt string
        """
        # Format context
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            paper_id = chunk.get('paper_id', 'unknown')
            text = chunk.get('text', '')
            context_parts.append(f"[Source {i} - Paper {paper_id}]\n{text}")
        
        context_str = "\n\n".join(context_parts)

        prompt = f"""You are a helpful research assistant. Answer the user's question based ONLY on the provided context from research papers.

Context from Research Papers:
{context_str}

User Question: {question}

Instructions:
- Provide a clear, accurate answer based on the context above
- Cite sources by referring to [Source N] when using information
- If the context doesn't contain enough information to answer, say so
- Be concise but thorough
- Use academic language appropriate for research discussion

Answer:"""
        
        return prompt
    
    def _build_graph_rag_prompt(self, question: str, context_chunks: List[dict], graph_nodes: List[dict]) -> str:
        """
        Build prompt for GraphRAG (hybrid retrieval)
        
        Args:
            question: User's question
            context_chunks: Text chunks from FAISS
            graph_nodes: Relevant nodes from Neo4j
            
        Returns:
            Formatted prompt string
        """
        # Format text context

        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            paper_id = chunk.get('paper_id', 'unknown')
            text = chunk.get('text', '')
            context_parts.append(f"[Text Source {i} - Paper {paper_id}]\n{text}")

        # Format graph context
        graph_parts = []
        for i, node in enumerate(graph_nodes, 1):
            node_type = node.get('node_type', 'Unknown')
            props = node.get('properties', {})

            if node_type == 'Paper':
                graph_parts.append(
                    f"[Graph Node {i}] Paper: {props.get('title', 'N/A')} "
                    f"(Year: {props.get('year', 'N/A')}, Authors: {props.get('authors', 'N/A')})"
                )
            elif node_type == 'Author':
                graph_parts.append(f"[Graph Node {i}] Author: {props.get('name', 'N/A')}")
            elif node_type == 'Concept':
                graph_parts.append(f"[Graph Node {i}] Concept/Topic: {props.get('name', 'N/A')}")
        
        context_str = "\n\n".join(context_parts)
        graph_str = "\n".join(graph_parts) if graph_parts else "No relevant graph connections found."

        prompt = f"""You are a research assistant with access to both full-text content and structured knowledge graph data.

Full-Text Context:
{context_str}

Knowledge Graph Context (papers, authors, concepts, citations):
{graph_str}

User Question: {question}

Instructions:
- Answer using BOTH the text content and graph relationships
- The graph shows structured connections (citations, authorship, topics)
- Cite text sources as [Text Source N] and graph data as [Graph Node N]
- Explain any relationships or connections from the graph
- If asked about citations, authors, or topics, emphasize graph data
- Be comprehensive and cite your sources

Answer:"""
        
        return prompt
            
    def _build_conversation_prompt(self, question: str, context_chunks: List[dict], conversation_history: str) -> str:
        """
        Build prompt for CAG (Context-Aware Generation with memory)
        
        Args:
            question: Current user question
            context_chunks: Retrieved text chunks
            conversation_history: Formatted past conversation
            
        Returns:
            Formatted prompt string
        """
        # Format context
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            paper_id = chunk.get('paper_id', 'unknown')
            text = chunk.get('text', '')
            context_parts.append(f"[Source {i} - Paper {paper_id}]\n{text}")
        
        context_str = "\n\n".join(context_parts)

        prompt = f"""You are a research assistant engaged in a multi-turn conversation. Use the conversation history to maintain context.

{conversation_history}

Relevant Research Context:
{context_str}

Current User Question: {question}

Instructions:
- Consider the conversation history when answering
- If the user refers to "it", "that", or "this", use context from previous turns
- Maintain continuity with previous answers
- Cite sources from the research context
- If the current question builds on previous topics, acknowledge that connection

Answer:"""
        
        return prompt

    def generate_answer(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """
        Generate answer using Gemini
        
        Args:
            prompt: Formatted prompt string
            max_tokens: Maximum response length
            temperature: Creativity (0.0-1.0)
            
        Returns:
            Generated answer text
        """
        if not self.configured:
            self.configure()
        
        if not self.configured:
            return "LLM service not configured. Please set GEMINI_API_KEY in environment."

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            )
            answer = response.text
            logger.info(f"Generated answer ({len(answer)} chars)")
            return answer
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"Error generating answer: {str(e)}"
    
    def generate_rag_answer(self, question: str, context_chunks: List[dict]) -> str:
        """Generate answer for standard RAG query"""
        prompt = self._build_rag_prompt(question, context_chunks)
        return self.generate_answer(prompt)
    
    def generate_graph_rag_answer(self, question: str, context_chunks: List[dict], graph_nodes: List[dict]) -> str:
        """Generate answer for GraphRAG query"""
        prompt = self._build_graph_rag_prompt(question, context_chunks, graph_nodes)
        return self.generate_answer(prompt)
    
    def generate_conversation_answer(self, question: str, context_chunks: List[dict], conversation_history: str) -> str:
        """Generate answer for conversational query with memory"""
        prompt = self._build_conversation_prompt(question, context_chunks, conversation_history)
        return self.generate_answer(prompt)

# Global instance
llm_service = LLMService()