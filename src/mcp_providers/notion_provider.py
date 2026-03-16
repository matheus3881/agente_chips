import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

def mcp_notion():
    return MultiServerMCPClient(
        {
            "notion": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@notionhq/notion-mcp-server"],
                "env": {"NOTION_TOKEN": os.getenv("NOTION_KEY")},
            }
        }
    )


