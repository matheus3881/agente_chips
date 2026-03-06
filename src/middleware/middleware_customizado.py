import traceback
import asyncio
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage


@wrap_tool_call
async def tool_erros(request, handler):
    """Lidar com erros de execução da ferramenta com mensagens personalizadas"""
    try:
        return await handler(request)
    except Exception as e:
        tool_name = await request.tool_call.get("name", "desconhecida")
        print(f"\n [ERRO TOOL: {tool_name}]\n{traceback.format_exc()}\n{'='*50}")

        return await ToolMessage(
            content=f"[TOOL_ERROR] Não foi possível executar '{tool_name}'. Motivo: {type(e).__name__}: {str(e)[:150]}",
            tool_call_id=request.tool_call["id"],
        )
