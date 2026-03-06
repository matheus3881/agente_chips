from langchain_mcp_adapters.client import MultiServerMCPClient


def mcp_playwright():
    return MultiServerMCPClient(
        {
            "playwright": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@playwright/mcp@latest", "--image-responses", "omit"],
            },
        }
    )
