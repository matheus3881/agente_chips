# utils/error_summarizer.py
import re

def summarize_error(e: Exception) -> str:
    error_type = type(e).__name__
    full_msg = str(e).strip().split("\n")[0][:200]

    friendly = {
        "TimeoutError":        "Timeout ao chamar a tool",
        "ConnectionError":     "Falha de conexão com a tool",
        "GraphRecursionError": "Agente entrou em loop (máx. iterações)",
        "ValueError":          "Argumento inválido enviado à tool",
        "KeyError":            "Resposta inesperada da tool",
        "ToolException":       "Erro interno da tool",
    }
    return friendly.get(error_type, f"{error_type}: {full_msg}")
