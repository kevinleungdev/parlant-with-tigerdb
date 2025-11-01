DOCS = [
    {
        "id": "POLICY-001",
        "title": "Refund Policy",
        "content": "You can get a refund or replacement within 30 days of delivery, as long as the item is in its original or unused condition."
    },
    {
        "id": "POLICY-002",
        "title": "Payment Policy",
        "content": "Customers have numerous payment options, including major credit and debit cards, gift cards, and various BNPL (buy now, pay later) plans."
    },
    {
        "id": "FAQ-001",
        "title": "Shipping Timeframe",
        "content": "Typically takes 3 or 5 business days, though free shipping on qualifying orders often has a 5 or 8 day delivery window."
    }
]

import json

from db import get_db
from jina import jina_client


def load_docs():
    with get_db() as conn:
        embeddings = jina_client.embed(
            [doc["content"] for doc in DOCS], task="retrieval.passage"
        )

        sql = '''INSERT INTO documents (id, title, content, embedding) VALUES ''' + \
              ', '.join(['(%s, %s, %s, %s)' for _ in embeddings])
        
        params = []
        for doc, emb in zip(DOCS, embeddings):
            params.extend([doc["id"], doc["title"], doc["content"], emb])

        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()

            print(f"Inserted {len(DOCS)} documents into the database.")


if __name__ == "__main__":
    load_docs()