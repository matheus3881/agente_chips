import asyncio
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from experiments.mcp.filesystem_provider import mcp_filesystem
from utils.error_summarizer import summarize_error

model = ChatOllama(model="qwen3.5:4b-q4_K_M", num_ctx=16384)

PROMPT = """
Você é um assistente que GENRENCIA pastas do DESKTOP.

Você pode APENAS ler e criar arquivos.
NUNCA deve ALTERAR ou DELETAR mesmo que seja pedido.
Caso peçam para ALTERAR ou DELETAR informe que 'não pode'.
Se não encontrar nenhum arquivo ou pasta indicada apenas responda 'não achei'.

"""

@tool
async def agent_filesystem(query):
    """USE para Gerencia arquivos podendo deletar, alterar, ler e criar.
    Assim como listar e procurar arquivos que forem pedidos.
    """
    tools = await mcp_filesystem().get_tools()
    agent = create_agent(model=model, tools=tools, system_prompt=PROMPT)

    try:
        response = await agent.ainvoke({"messages":[{"role": "user", "content": query}]})

        return response['messages'][-1].content
    
    except Exception as e:
        import traceback
        print(f"\n[ERRO agent_github]\n{traceback.format_exc()}\n{'='*50}")

        resumo = summarize_error(e)
        return f"[TOOL_ERROR] Não foi possível concluir. Motivo: {resumo}"


