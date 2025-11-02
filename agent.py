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


@p.tool
def search_relevant_docs(context: p.ToolContext, query: str, to_k: int = 5) -> p.ToolResult:
    print(f"Excute a vector search with the user's query '{query}'")

    with get_db() as conn:
        search_tool = MultiSearchTool(conn, jina_client)

        results = search_tool.hybrid_search(query)
        
        hits = []
        for result in results:
            hits.append({
                "doc_id": result["id"],
                "title": result["title"],
                "content": result["content"],
                "score": result["score"]
            })
        print(f"The retrieved information: {hits}")
        
        return p.ToolResult({"information": hits})


async def main():
    async with p.Server() as server:
        agent = await server.create_agent(
            name="Otto Carmen",
            description="You work at a online store"
        )

        # Create a `current-datetime` variable for templates or logs
        @p.tool
        async def get_current_datetime(context: p.ToolContext) -> p.ToolResult:
            from datetime import datetime
            return p.ToolResult({ "now": datetime.now().isoformat() })
        await agent.create_variable(name="current-datetime", tool=get_current_datetime)


        # Initiate a vector search if the user's query is relevant to online shopping policies
        await agent.create_guideline(
            condition="The user's input is classified as a factual inquiry concerning store policies, including refunds, payments, or shippings",
            action=(
                "1. **Initiate a `search_relevant_docs`** to locate the relevant policy information based on the user's query.\n"
                "2. **If clear information is retrieved:** Formulate a helpful answer by quoting the most pertinent sentences from our policy documents. Reference the source by its `doc_id` or `title` (e.g. \"According to our 'Refund Policy' page...\")\n"
                "3. **If the retrieved information is ambiguous or incomplete:** proactively ask a follow-up question to clarify the user's needs. For example, \"Could you please specify if you're asking about domestic or international shipping?\". \n"
            ),
            tools=[search_relevant_docs]
        )


asyncio.run(main())