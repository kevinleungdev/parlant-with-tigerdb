import os
import asyncio
import parlant.sdk as p

from dotenv import load_dotenv

load_dotenv()

if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")


async def main():
    async with p.Server() as server:
        agent = await server.create_agent(
            name="Otto Carmen",
            description="You work at a car dealership"
        )


asyncio.run(main())