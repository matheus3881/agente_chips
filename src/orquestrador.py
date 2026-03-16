import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_cerebras import ChatCerebras
from langgraph.checkpoint.memory import InMemorySaver

from langfuse.langchain import CallbackHandler

from agents.tavily_agent import agent_tavily
from agents.github_agent import agent_github

from middleware.middleware_customizado import tool_erros


from middleware.cortar_mensagem import cortar_mensagens
from agents.notion_agent import agent_notion
from utils.error_summarizer import summarize_error


load_dotenv()
langfuse_handler = CallbackHandler()

model = ChatCerebras(model="qwen-3-235b-a22b-instruct-2507", api_key=os.getenv("CEREBRAS_API_KEY"))
# model = ChatOllama(model="gpt-oss:20b", num_ctx=16384)
tools = [agent_tavily, agent_github, agent_notion]

PROMPT = f"""
DATA ATUAL: {datetime.now()}
Você é um agente orquestrador que possui subagentes sob seu comando.
Responda em tópicos quando necessário e NUNCA em tabelas, pois as respostas são exibidas no Telegram.
Cada subagente é especializado em um domínio específico.

SUBAGENTES DISPONÍVEIS:
- 'agent_tavily': pesquisas na web, notícias e informações atualizadas.
- 'agent_github': gerenciar repositórios, issues, pull requests e código no GitHub.
- 'agent_notion': gerenciar páginas, databases e conteúdo no Notion.

REGRAS:
- SEMPRE delegue para o subagente correto. Nunca execute diretamente o que um subagente pode fazer.
- Se a tarefa envolver múltiplos domínios, acione os subagentes necessários em sequência.
- Nunca diga que não tem acesso a algo que um subagente pode resolver.
- Nunca oriente o usuário a fazer manualmente o que um subagente pode executar.

FLUXO DE DECISÃO:
1. Identifique o domínio da tarefa solicitada pelo usuário.
2. Acione o subagente correspondente com uma instrução clara e objetiva.
3. Consolide as respostas dos subagentes e apresente ao usuário de forma organizada.

FORMATO DE RESPOSTA:
- Use tópicos e listas simples compatíveis com Telegram (sem markdown de tabela).
- Seja objetivo e direto. Evite respostas longas sem necessidade.
- Sempre confirme ao usuário o que foi executado ao final de uma ação.
"""


orquestrador = create_agent(
    model=model, tools=tools, system_prompt=PROMPT, middleware=[tool_erros, cortar_mensagens], checkpointer=InMemorySaver()
)


async def agent_orquestrador(query, chat_id):
    try:
        response = await orquestrador.ainvoke(
            {"messages": [{"role": "user", "content": query}]},
            config={
                "callbacks": [langfuse_handler],
                "configurable": {"thread_id": chat_id}
            },
        )

        res = response["messages"][-1].content
        print(res)
        return res

    except Exception as e:
        import traceback

        print(f"\n[ERRO ORQUESTRADOR]\n{traceback.format_exc()}\n{'='*50}")

        resumo = summarize_error(e)
        # Retorna mensagem amigável pro Telegram em vez de silêncio
        return (
            f"⚠️ Não consegui completar sua solicitação.\n"
            f"Motivo: {resumo}\n\n"
            f"Tente novamente ou reformule o pedido."
        )


# asyncio.run(agent_orquestrador())
