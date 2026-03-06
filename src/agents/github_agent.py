import asyncio
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from mcp_providers.github_provider import mcp_github
from utils.error_summarizer import summarize_error

model = ChatOllama(model="qwen3.5:4b-q4_K_M", num_ctx=16384)

PROMPT = """
Você é um agente com acesso direto à API do GitHub através de tools.
Você TEM credenciais configuradas e PODE executar ações reais no GitHub.

REGRAS:
- SEMPRE use as tools disponíveis para responder. Nunca diga que não tem acesso.
- Para listar repositórios do usuário autenticado:
  1. Chame get_me para obter o username
  2. Use search_repositories com query "user:<username>"
- Nunca oriente o usuário a fazer manualmente o que você pode fazer com tools.
- Nunca sugira usar curl, token manual ou acessar o site.
"""


@tool
async def agent_github(query):
    """Use para gerenciar ações no github.

    Exemplo: criar repositorios ou arquivos, buscar informações..."""
    tools = await mcp_github().get_tools()
    agent = create_agent(model=model, tools=tools, system_prompt=PROMPT)

    try:
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        return response["messages"][-1].content

    except Exception as e:

        import traceback
        print(f"\n[ERRO agent_github]\n{traceback.format_exc()}\n{'='*50}")

        resumo = summarize_error(e)
        return f"[TOOL_ERROR] Não foi possível concluir. Motivo: {resumo}"
