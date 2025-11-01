from typing import Any


class MultiSearchTool:
    
    def __init__(self, connection, jina_client):
        self.conn = connection
        self.jina = jina_client


    def extract_search(self, query: str, limit: int = 5):
        """Extract keyword matching for specific terms, names, dates"""
        with self.conn.cursor() as cur:
            # Search for exact phrase and important keywords
            cur.execute("""
                SELECT id, title, content, 1.0 AS score, 'exact' AS search_type
                    FROM documents
                    WHERE content LIKE %s
                    ORDER BY char_length(content)  -- Prefr shorter, more focused articles
                    LIMIT %s
            """, (f"%{query}%", limit))
            return cur.fetchall()
        

    def fulltext_search(self, query: str, limit: int = 5):
        """PostgreSQL full-text search with ranking"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, content,
                       ts_rank_cd(
                            to_tsvector('english', content), 
                            plainto_tsquery(%s)
                        ) AS score,
                       'fulltext' AS search_type
                FROM documents,
                     plainto_tsquery('english', %s) AS query
                WHERE to_tsvector('english', content) @@ query
                ORDER BY score DESC
                LIMIT %s
            """, (query, query, limit))
            return cur.fetchall()
        
    
    def semantic_search(self, query: str, limit: int=5):
        """Vector-based semantic search using Jina embeddings"""
        try:
            # Generate query embedding
            query_embeddings = self.jina.embed([query], task="retrieval.passage")

            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, content,
                           1 - (embedding <=> %s::vector) AS score,
                           'semantic' AS search_type
                    FROM documents
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (
                    query_embeddings[0], 
                    query_embeddings[0], 
                    limit
                ))
                return cur.fetchall()
            
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return []
        

    def combine_and_deduplicate(self, *result_sets):
        """Combine results from multiple search methods, removing duplicaties"""
        seen_ids = set()
        combined = []

        # Process results in order of priority
        for results in result_sets:
            for result in results:
                doc_id = result[0]
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    combined.append({
                        "id": doc_id,
                        "title": result[1],
                        "content": result[2],
                        "score": result[3],
                        "search_type": result[4]
                    })

        return combined
    

    def rerank_results(
            self, query: str, results: list[Any], top_k: int = 5
        ):
        """Use Jina's rerank API for final relevance scoring"""
        if not results:
            return []
        
        # Prepare documents for reranking (truncate long articles)
        # Take first 2000 chars to stay within rerank limits
        documents = [result["content"][:2000] for result in results]

        try:
            rerank_response = self.jina.rerank(
                query, documents=documents, top_k=top_k
            )

            # Map reranked results back to original data
            reranked = []
            for rerank_result in rerank_response:
                original_idx = rerank_result["index"]

                result = results[original_idx].copy()
                result["rerank_score"] = rerank_result["relevance_score"]

                reranked.append(result)

            return reranked

        except Exception as e:
            print(f"Reranking error: {e}")
            return results[:top_k]


    def hybrid_search(self, query: str, limit: int = 5):
        """Main hybrid search function combining all methods"""
        # Cast wide net with all search methods
        extract_results = self.extract_search(query, limit=limit)
        fulltext_results = self.fulltext_search(query, limit=limit)
        semantic_results = self.semantic_search(query, limit=limit)

        # Combine and deduplicate (extract matches prioritized first)
        combined = self.combine_and_deduplicate(
            extract_results,
            fulltext_results,
            semantic_results
        )

        # Rerank for final relevance
        final_results = self.rerank_results(query, combined, limit)

        return final_results
