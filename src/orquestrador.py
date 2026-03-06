import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_cerebras import ChatCerebras
from langgraph.checkpoint.memory import InMemorySaver

from langfuse.langchain import CallbackHandler

from agents.filesystem_agent import agent_filesystem
from agents.tavily_agent import agent_tavily
from agents.github_agent import agent_github

from middleware.middleware_customizado import tool_erros


from middleware.cortar_mensagem import cortar_mensagens
from utils.error_summarizer import summarize_error


load_dotenv()
langfuse_handler = CallbackHandler()

model = ChatCerebras(model="gpt-oss-120b", api_key=os.getenv("CEREBRAS_API_KEY"))
# model = ChatOllama(model="gpt-oss:20b", num_ctx=16384)
tools = [agent_filesystem, agent_tavily, agent_github]

PROMPT = f"""
DATA ATUAL: {datetime.now()}
Você é uma agente orquestrador que possui subagentes sobe seu comando.
Responda em tópicos quando necessário e não em tabelas pois as respostas são exibidas no TELEGRAM.
Cada subagente é próprio para uma tarefa/domínio especializado.

Para gerenciar arquivos use: 'agent_filesystem'.
Para agent_filesystem use: 'query': 'crie arquivo nome.txt com conteúdo aqui'

Para faze pesquisas web use: 'agent_tavily'.
Para gerenciar o Github use: 'agent_github'.
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
