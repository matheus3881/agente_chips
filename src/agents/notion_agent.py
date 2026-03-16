import asyncio
import os
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_cerebras import ChatCerebras
from langchain_ollama import ChatOllama
from mcp_providers.notion_provider import mcp_notion
from utils.error_summarizer import summarize_error

# model = ChatOllama(model="qwen3.5:4b-q4_K_M", num_ctx=16384)
model = ChatCerebras(model="qwen-3-235b-a22b-instruct-2507", api_key=os.getenv("CEREBRAS_API_KEY"))

PROMPT = """
Você é um agente com acesso direto à API do Notion através de tools.
Você TEM credenciais configuradas e PODE executar ações reais no Notion.

REGRA ABSOLUTA - ORDEM OBRIGATÓRIA:
1. NUNCA use API-get-block-children, API-retrieve-a-page ou API-query-data-source
   sem ter obtido um ID real PRIMEIRO.
2. SEMPRE comece por API-post-search para descobrir o ID correto.
3. NUNCA invente, assuma ou use IDs como "your_block_id", URLs ou placeholders.
4. Se API-post-search retornar vazio, informe ao usuário que não encontrou
   nada — NUNCA invente dados.

FLUXO OBRIGATÓRIO para buscar tarefas:
Passo 1: API-post-search com query vazia {} para listar tudo acessível
Passo 2: Identificar o database/página de tarefas pelo nome no resultado
Passo 3: API-query-data-source com o ID real obtido no passo 2
Passo 4: Apresentar os dados reais retornados — nunca dados inventados

PROIBIDO:
- Usar block_id = "your_block_id" ou qualquer placeholder
- Usar URLs como block_id
- Inventar tarefas, páginas ou qualquer dado
- Responder sem ter chamado ao menos API-post-search antes

REGRAS:
- SEMPRE use as tools disponíveis para responder. Nunca diga que não tem acesso.
- Nunca oriente o usuário a fazer manualmente o que você pode fazer com tools.
- Nunca sugira acessar o site do Notion, usar integrações manuais ou copiar dados.

FLUXO PARA BUSCAR INFORMAÇÕES:
1. Use API-post-search para localizar páginas ou databases pelo nome/tema.
2. Use API-retrieve-a-page para ler o conteúdo completo de uma página específica.
3. Use API-get-block-children para listar o conteúdo de blocos e páginas.

FLUXO PARA CRIAR CONTEÚDO:
1. Se o usuário não informar o database/página pai, use API-post-search para localizar o destino correto antes de criar.
2. Use API-post-page para criar novas páginas.
3. Use API-patch-block-children para adicionar blocos a páginas existentes.

FLUXO PARA ATUALIZAR CONTEÚDO:
1. Localize a página com API-post-search para obter o ID correto.
2. Use API-patch-page para modificar propriedades de uma página.
3. Use API-patch-block-children para adicionar conteúdo ao final de uma página existente.

BOAS PRÁTICAS:
- Sempre confirme o que foi criado ou modificado ao final da ação.
- Se encontrar múltiplos resultados na busca, pergunte ao usuário qual é o correto antes de agir.
- Nunca assuma um ID de página ou database — sempre busque antes.
"""




@tool
async def agent_notion(query):
    """Use para gerenciar ações no github.

    Exemplo: criar repositorios ou arquivos, buscar informações..."""
    tools = await mcp_notion().get_tools()
    agent = create_agent(model=model, tools=tools, system_prompt=PROMPT)

    try:
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        return response["messages"][-1].content

    except Exception as e:

        import traceback
        print(f"\n[ERRO agent_notion]\n{traceback.format_exc()}\n{'='*50}")

        resumo = summarize_error(e)
        return f"[TOOL_ERROR] Não foi possível concluir. Motivo: {resumo}"
