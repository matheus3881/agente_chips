import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import datetime
from langchain_mcp_adapters.client import MultiServerMCPClient
from requests import session

server_params = StdioServerParameters(
    command='python',
    args = ['src/mcp/mcp_math.py'],
    env= None
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await load_mcp_tools(session)

            print("MCP tools:", [tool.name for tool in mcp_tools])

            llm = ChatOllama(model="qwen3:4b-instruct-2507-q4_K_M", temperature=0)

            agent = create_agent(llm, mcp_tools)

            response = await agent.ainvoke({"messages": "what's (5 + 5) x 10?"})

            print('Agent response:', response['messages'][-1].content)


if __name__ == '__main__':
    asyncio.run(main())

        