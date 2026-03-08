# Agente JurCERJA

Assistente multiagente com interface via Telegram para orquestrar tarefas de pesquisa web, GitHub e filesystem.
O projeto usa um agente principal (orquestrador) que delega para subagentes especializados.

## Funcionalidades

- Resposta a mensagens de texto no Telegram
- Transcricao de audio (voz) para texto com `faster-whisper`
- Orquestracao de subagentes por dominio:
- `agent_tavily`: pesquisas web
- `agent_github`: acoes em GitHub via MCP
- `agent_filesystem`: leitura e criacao de arquivos em diretorio permitido via MCP
- Middleware para tratamento de erros e controle de historico de mensagens

## Arquitetura (resumo)

- Entrada Telegram: `src/tele.py`
- Orquestrador principal: `src/orquestrador.py`
- Subagentes: `src/agents/`
- Providers MCP: `src/mcp_providers/`
- Middleware: `src/middleware/`

Fluxo:
1. Usuario envia texto/audio no Telegram.
2. `tele.py` recebe e, se necessario, transcreve audio.
3. `orquestrador.py` decide qual subagente chamar.
4. Subagente executa tools MCP e retorna resposta final ao Telegram.

## Requisitos

- Python 3.12+
- `pip`
- Node.js + `npx` (necessario para MCP de filesystem/playwright)
- Tokens/API keys configurados em `.env`

## Instalacao

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuracao

1. Copie `.env.example` para `.env`
2. Preencha as variaveis necessarias

Variaveis mais importantes:
- `TELEGRAM_TOKEN`
- `CEREBRAS_API_KEY`
- `TAVILY_API_KEY`
- `GITHUB_API_KEY`
- `FILESYSTEM_ROOT` (ex.: `C:\Users\BOBO\Desktop`)

Observabilidade (opcional):
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_BASE_URL`

## Execucao

```bash
python src/tele.py
```

## Estrutura de pastas

```text
src/
  agents/          # subagentes por dominio
  mcp_providers/   # conexao com servidores MCP
  middleware/      # tratamento de erro e gerenciamento de contexto
  utils/           # utilitarios
  tele.py          # bot Telegram
  orquestrador.py  # agente principal

experiments/
  lang_graph/      # provas de conceito e estudos
  mcp/             # testes de aprendizado com MCP
```

## Experimentos

As pastas em `experiments/` sao POCs e estudos tecnicos.
Elas nao fazem parte do fluxo principal de execucao do bot em producao.

## Limitacoes atuais

- Dependencia de APIs externas (latencia e disponibilidade)
- Necessidade de configuracao correta de chaves/tokens para execucao completa

## Proximos passos

- Adicionar testes automatizados (unitarios e integracao)
- Criar pipeline de CI (lint + testes + validacao de build)
- Melhorar documentacao das tools e contratos de entrada/saida
