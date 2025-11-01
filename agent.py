import os
import asyncio
import parlant.sdk as p

from dotenv import load_dotenv
from db import get_db
from jina import jina_client
from search import MultiSearchTool


load_dotenv()

if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")


def search_relevant_docs(query: str):
    with get_db() as conn:
        search_tool = MultiSearchTool(conn, jina_client)
        return search_tool.hybrid_search(query)


async def main():
    async with p.Server() as server:
        agent = await server.create_agent(
            name="Otto Carmen",
            description="You work at a car dealership"
        )


search_relevant_docs("what's your refund policy")

# asyncio.run(main())