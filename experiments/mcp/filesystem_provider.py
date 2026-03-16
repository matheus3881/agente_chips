import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

def mcp_filesystem():
    root_dir = os.getenv("FILESYSTEM_ROOT", os.path.expanduser("~/Desktop"))
    return MultiServerMCPClient(
        {
            "filesystem": {
                "transport": "stdio",
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    root_dir,
                ],
            },
        }
    )
