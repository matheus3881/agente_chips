# Agente Chips

Assistente multiagente com interface via Telegram para orquestrar pesquisas web, operacoes no GitHub e consultas/acoes no Notion.
O projeto usa um agente principal que delega tarefas para subagentes especializados via MCP.

## Funcionalidades

- Recebe mensagens de texto no Telegram
- Recebe mensagens de voz e faz transcricao com `faster-whisper`
- Mantem contexto por conversa usando `thread_id` do chat
- Orquestra subagentes especializados por dominio
- Trata erros de tools com mensagens resumidas para o usuario
- Reduz historico enviado ao modelo para caber na janela de contexto

Subagentes ativos no fluxo principal:
- `agent_tavily`: pesquisas web e informacoes atualizadas
- `agent_github`: acoes reais no GitHub via MCP
- `agent_notion`: leitura, busca, criacao e atualizacao de conteudo no Notion via MCP

## Arquitetura

- Entrada Telegram: `src/tele.py`
- Orquestrador principal: `src/orquestrador.py`
- Subagentes: `src/agents/`
- Providers MCP: `src/mcp_providers/`
- Middleware: `src/middleware/`
- Utilitarios: `src/utils/`

Fluxo principal:
1. O usuario envia texto ou audio no Telegram.
2. `src/tele.py` recebe a mensagem.
3. Se for audio, `src/agents/voice_agent.py` transcreve para texto.
4. `src/orquestrador.py` identifica o dominio da tarefa.
5. O orquestrador delega para `agent_tavily`, `agent_github` e/ou `agent_notion`.
6. O subagente usa seu provider MCP correspondente e devolve a resposta final ao Telegram.

## Servicos MCP documentados

### `agent_notion`

Arquivo: `src/agents/notion_agent.py`

Responsavel por executar instrucoes relacionadas ao Notion.
Ele cria um agente especializado com tools carregadas pelo provider `mcp_notion`.

Capacidades documentadas no prompt do agente:
- localizar paginas e databases com busca
- consultar paginas e blocos existentes
- criar novas paginas
- adicionar blocos em paginas existentes
- atualizar propriedades de paginas

Regra importante do fluxo:
- o agente deve buscar IDs reais no Notion antes de consultar ou alterar conteudo

### `mcp_notion`

Arquivo: `src/mcp_providers/notion_provider.py`

Provider MCP responsavel por conectar o projeto ao servidor oficial do Notion via `npx`.

Implementacao atual:
- transporte `stdio`
- comando `npx -y @notionhq/notion-mcp-server`
- autenticacao por `NOTION_KEY`

Esse provider e usado exclusivamente por `agent_notion`.

## Integracoes e providers

- `src/mcp_providers/tavily_provider.py`
  - conecta no MCP HTTP da Tavily usando `TAVILY_API_KEY`
- `src/mcp_providers/github_provider.py`
  - conecta no MCP HTTP do GitHub usando `GITHUB_API_KEY`
- `src/mcp_providers/notion_provider.py`
  - sobe o servidor MCP do Notion com `npx` usando `NOTION_KEY`

## Requisitos

- Python 3.12+
- `pip`
- Node.js + `npx`
- Tokens e chaves configurados em `.env`

`Node.js` e `npx` sao necessarios porque o provider `mcp_notion` executa o servidor `@notionhq/notion-mcp-server`.

## Instalacao

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuracao

1. Copie `.env.example` para `.env`
2. Preencha as variaveis necessarias

Variaveis principais:
- `TELEGRAM_TOKEN`
- `CEREBRAS_API_KEY`
- `TAVILY_API_KEY`
- `GITHUB_API_KEY`
- `NOTION_KEY`

Observabilidade:
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_BASE_URL`

Variaveis adicionais presentes no exemplo:
- `GROQ_API_KEY`
- `NOTION_PAGE_ID`
- `DATABASE`
- `DATA_SOURCE_ID`
- `FILESYSTEM_ROOT`

Observacao:
- `FILESYSTEM_ROOT` permanece apenas para experimentos e nao faz parte do fluxo principal atual

## Execucao

```bash
python src/tele.py
```

## Estrutura de pastas

```text
src/
  agents/          # subagentes do fluxo principal
  mcp_providers/   # integracoes MCP dos subagentes
  middleware/      # tratamento de erros e corte de historico
  utils/           # utilitarios
  tele.py          # bot Telegram
  orquestrador.py  # agente principal

experiments/
  lang_graph/      # estudos e POCs com LangGraph
  mcp/             # testes de aprendizado com MCP
  filesystem_agent.py
  playwright_agent.py
```

## Experimentos

O suporte a filesystem e Playwright nao esta no fluxo principal atual.
Esses artefatos foram movidos para `experiments/` e servem como estudo ou prova de conceito.

## Limitacoes atuais

- Dependencia de APIs e servicos externos
- Necessidade de credenciais validas para cada integracao
- O bot usa polling no Telegram, sem webhook
- A transcricao de voz roda localmente em CPU

## Proximos passos

- Adicionar testes automatizados
- Criar pipeline de CI
- Melhorar a documentacao das tools MCP e dos contratos entre orquestrador e subagentes
