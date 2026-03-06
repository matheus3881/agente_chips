import asyncio
from datetime import datetime
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langsmith import expect
from mcp_providers.tavily_provider import mcp_tavily
from utils.error_summarizer import summarize_error

model = ChatOllama(model="qwen3.5:4b-q4_K_M", num_ctx=16384).bind_tools([], tool_choice="any")

PROMPT = f"""
Você é um agente de PESQUISAS WEB.
Data atual: {datetime.now().strftime("%d/%m/%Y")}
Ao usar tavily_search:
- OBRIGATÓRIO: use apenas os campos 'query' e opcionalmente 'max_results'
- NUNCA preencha 'topic', 'country', 'search_depth' ou outros campos
"""


@tool
async def agent_tavily(query):
    """Use para Fazer pesquisas WEB e trazer informações que desconhece"""
    tools = await mcp_tavily().get_tools()
    agent = create_agent(model=model, tools=tools, system_prompt=PROMPT)

    try:
        response = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
        return response['messages'][-1].content
    
    except Exception as e:
        # Log completo só no seu console
        import traceback
        print(f"\n[ERRO agent_github]\n{traceback.format_exc()}\n{'='*50}")

        # Retorna resumo limpo pro orquestrador
        resumo = summarize_error(e)
        return f"[TOOL_ERROR] Não foi possível concluir. Motivo: {resumo}"
