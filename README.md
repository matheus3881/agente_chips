# Agente JurCERJA

Assistente multiagente com interface via Telegram, focado em orquestrar tarefas de pesquisa web, GitHub e filesystem.
O projeto usa um agente principal (orquestrador) que delega para subagentes especializados conforme a intenção da mensagem.

## Funcionalidades

- Resposta a mensagens de texto no Telegram
- Transcrição de áudio (voz) para texto com `faster-whisper`
- Orquestração de subagentes por domínio:
- `agent_tavily`: pesquisas web
- `agent_github`: ações em GitHub via MCP
- `agent_filesystem`: leitura/criação de arquivos em diretório permitido via MCP
- Middleware para tratamento de erros e controle de histórico de mensagens

## Arquitetura (resumo)

- Entrada Telegram: `src/tele.py`
- Orquestrador principal: `src/orquestrador.py`
- Subagentes: `src/agents/`
- Providers MCP: `src/mcp_providers/`
- Middleware: `src/middleware/`

Fluxo:
1. Usuário envia texto/áudio no Telegram.
2. `tele.py` recebe e, se necessário, transcreve áudio.
3. `orquestrador.py` decide qual subagente chamar.
4. Subagente executa tools MCP e retorna resposta final ao Telegram.

## Requisitos

- Python 3.12+
- `pip`
- Node.js + `npx` (necessário para MCP de filesystem/playwright)
- Tokens/API keys configurados em `.env`

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração

1. Copie `.env.example` para `.env`
2. Preencha as variáveis necessárias

Variáveis mais importantes:
- `TELEGRAM_TOKEN`
- `CEREBRAS_API_KEY`
- `TAVILY_API_KEY`
- `GITHUB_API_KEY`
- `FILESYSTEM_ROOT` (ex.: `C:\Users\BOBO\Desktop`)

Observabilidade (opcional):
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_BASE_URL`

## Execução

```bash
python src/tele.py
```

## Estrutura de pastas

```text
src/
  agents/          # subagentes por domínio
  mcp_providers/   # conexão com servidores MCP
  middleware/      # tratamento de erro e gerenciamento de contexto
  utils/           # utilitários
  tele.py          # bot Telegram
  orquestrador.py  # agente principal
```

## Limitações atuais

- Dependência de APIs externas (latência e disponibilidade)
- Necessidade de configuração correta de chaves/tokens para execução completa
- Alguns módulos em `src/lang_graph` e `src/mcp` são experimentais (POCs)

## Próximos passos

- Adicionar testes automatizados (unitários e integração)
- Criar pipeline de CI (lint + testes + validação de build)
- Melhorar documentação das tools e contratos de entrada/saída
