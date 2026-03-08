import asyncio

from experiments.mcp.playwright_provider import mcp_playwright

async def create_playwright_agent():
    tools = await mcp_playwright().get_tools()
    print(f"Tools: {[t.name for t in tools]}")

asyncio.run(create_playwright_agent())