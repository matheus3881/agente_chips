import os

from dotenv import load_dotenv
import httpx
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
def no_ssl_httpx_factory(**kwargs):
    kwargs.pop("verify", None)  # remove verify se vier nos kwargs
    return httpx.AsyncClient(verify=False, **kwargs)

def mcp_tavily():
    return MultiServerMCPClient(
        {
            "tavily": {
                "transport": "http",
                "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={os.getenv('TAVILY_API_KEY')}",
                "httpx_client_factory": no_ssl_httpx_factory,
            },
        }
    )
