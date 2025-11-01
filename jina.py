import requests
import json

from env import JINA_API_KEY


if JINA_API_KEY is None:
    raise ValueError("JINA_API_KEY not found in environment variables")


class JinaClient:

    def __init__(self, api_key=JINA_API_KEY):
        self.base_url = "https://api.jina.ai/v1/"
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }


    def embed(self, documents: list[str], task="text-matching") -> list[float]:
        data = {
            "model": "jina-embeddings-v3",
            "task": task,
            "input": documents
        }

        res = requests.post(
            self.base_url + "embeddings",
            headers=self.headers,
            json=data
        )

        return [item["embedding"] for item in res.json()["data"]]
    

    def rerank(self, query: str, documents: list[str], top_k: int = 5):
        data = {
            "model": "jina-reranker-v2-base-multilingual",
            "query": query,
            "top_n": top_k,
            "documents": documents,
            "return_documents": False
        }

        res = requests.post(
            self.base_url + "rerank",
            headers=self.headers,
            data=json.dumps(data)
        )
    
        if res.status_code == 200:
            return [
                { 
                    "index": result["index"],
                    "relevance_score": result["relevance_score"] 
                } for result in res.json()["results"]
            ]
        else:
            print(f"Jina rerank status: {res.status_code}, message: {res.text}")
            return []


jina_client = JinaClient()