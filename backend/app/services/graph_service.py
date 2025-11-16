from typing import List, Dict, Any
import logging
from ..core.database import neo4j_conn

logger = logging.getLogger(__name__)

class GraphService:
    """Service for Neo4j graph database operations"""

    def search_papers_by_keyword(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for papers containing a keyword in title or abstract

        Args:
            keyword: Search term
            limit: Max number of results

        Returns:
            List of paper nodes with properties
        """
        query = """
                MATCH (p:Paper)
                WHERE toLower(p.title) CONTAINS toLower($keyword)
                   OR toLower(p.abstract) CONTAINS toLower($keyword)
                RETURN p.id AS id, p.title AS title, p.authors AS authors, 
                       p.year AS year, p.abstract AS abstract
                LIMIT $limit
                """

        with neo4j_conn.get_session() as session:
            result = session.run(query, keyword=keyword, limit=limit)
            papers = [dict(record) for record in result]

        logger.info(f"Found {len(papers)} papers for keyword: '{keyword}'")
        return papers

    def get_citations(self, paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get papers cited by a given paper

        Args:
            paper_id: Paper identifier
            limit: Max number of citations

        Returns:
            List of cited paper nodes
        """
        query = """
                MATCH (p:Paper {id: $paper_id})-[:CITES]->(cited:Paper)
                RETURN cited.id AS id, cited.title AS title, cited.year AS year
                LIMIT $limit
                """

        with neo4j_conn.get_session() as session:
            result = session.run(query, paper_id=paper_id, limit=limit)
            citations = [dict(record) for record in result]

        return citations

    def get_papers_by_author(self, author_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find papers by a specific author

        Args:
            author_name: Author's name
            limit: Max results

        Returns:
            List of papers
        """
        query = """
        MATCH (a:Author)-[:AUTHORED_BY]-(p:Paper)
        WHERE toLower(a.name) CONTAINS toLower($author_name)
        RETURN p.id AS id, p.title AS title, p.year AS year, a.name AS author
        LIMIT $limit
        """

        with neo4j_conn.get_session() as session:
            result = session.run(query, author_name=author_name, limit=limit)
            papers = [dict(record) for record in result]

        return papers

    def get_papers_by_topic(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find papers related to a topic/concept

        Args:
            topic: Topic or concept name
            limit: Max results

        Returns:
            List of papers
        """
        query = """
        MATCH (p:Paper)-[:HAS_TOPIC]->(c:Concept)
        WHERE toLower(c.name) CONTAINS toLower($topic)
        RETURN p.id AS id, p.title AS title, p.abstract AS abstract, c.name AS concept
        LIMIT $limit
        """

        with neo4j_conn.get_session() as session:
            result = session.run(query, topic=topic, limit=limit)
            papers = [dict(record) for record in result]

        return papers

    def add_paper(self, paper_data: dict):
        """
        Add a new paper node to the graph

        Args:
            paper_data: Dict with id, title, authors, year, abstract
        """
        query = """
        MERGE (p:Paper {id: $id})
        SET p.title = $title,
            p.authors = $authors,
            p.year = $year,
            p.abstract = $abstract
        RETURN p
        """

        with neo4j_conn.get_session() as session:
            session.run(query, **paper_data)

        logger.info(f"Added paper: {paper_data.get('title')}")

    def get_graph_stats(self) -> dict:
        """Get statistics about the knowledge graph"""
        query = """
        MATCH (p:Paper) 
        WITH count(p) AS paperCount
        MATCH (a:Author)
        WITH paperCount, count(a) AS authorCount
        MATCH ()-[r:CITES]->()
        RETURN paperCount, authorCount, count(r) AS citationCount
        """

        with neo4j_conn.get_session() as session:
            result = session.run(query)
            record = result.single()

            if record:
                return {
                    'papers': record['paperCount'],
                    'authors': record['authorCount'],
                    'citations': record['citationCount']
                }
            return {'papers': 0, 'authors': 0, 'citations': 0}

# Global instance
graph_service = GraphService()