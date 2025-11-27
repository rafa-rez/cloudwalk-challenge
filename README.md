# InfinitePay Swarm Intelligence

**Orquestração Multi‑Agente com Memória Persistente, RAG e Roteamento Inteligente**

Este repositório contém uma Prova de Conceito (PoC) de uma arquitetura de atendimento ao cliente baseada em IA Generativa. A solução centraliza o roteamento em um *Router* que distribui as solicitações para agentes especialistas, garantindo tratamento diferenciado para dúvidas de produto, problemas técnicos e tentativas de ataque.

---

## Visão Geral

O sistema opera como um grafo de estado (*StateGraph*) utilizando LangGraph. A lógica de decisão segue o fluxo abaixo:

1. **Input & Segurança** — A mensagem do usuário passa por um guardrail (checagem hardcoded de palavras-chave) para bloquear injeção de prompt e outros ataques antes de invocar o LLM.
2. **Router (Cérebro)** — Analisa a intenção da última mensagem (com lógica anti‑bias) e decide qual agente especialista acionar.
3. **Agentes Especialistas** — Cada agente responde a um domínio específico do problema.
4. **Personality Layer** — Camada final que normaliza o tom de voz (sério para segurança; leve para atendimento).

---

## Agentes (Resumo)

- **Knowledge Agent** — Especialista em produtos e taxas. Utiliza RAG com ChromaDB e busca na web (ex.: DuckDuckGo). Sempre cita fontes quando necessário.
- **Support Agent** — Especialista em conta e transações. Acessa o banco de dados mockado para verificar saldo, status de Pix e bloqueios; serve como interface de dados.
- **Guardrail Agent** — Intercepta toxicidade e ataques; remove entradas maliciosas da memória para não contaminar o contexto.
- **Human Handoff** — Detecta quando o caso precisa ser transferido para um atendente humano.
- **Fallback Agent** — Trata mensagens ininteligíveis ou fora do escopo com respostas educadas que reorientam o usuário.

---

## Funcionalidades Principais

- **Backend**: FastAPI + LangGraph.
- **Memória Persistente**: Armazena contexto por `thread_id`, com lógica para "esquecer" entradas maliciosas.
- **Roteamento Contextual**: Permite mudança rápida de assunto sem ficar preso ao contexto anterior.
- **RAG & Tools**: Integração com ChromaDB e ferramentas Python para consulta a dados simulados e busca.
- **Segurança**: Dupla proteção — checagem de palavras‑chave pré‑LLM e prompts de guardrail.
- **Frontend**: Streamlit com visualização tipo "circuit board" mostrando qual agente está ativo em tempo real.
- **Bateria de Testes (QA)**: Cenários automatizados — Happy Path, erros, ataques — rodáveis via interface.

---

## Stack Tecnológica

- Linguagem: **Python 3.10**
- Orquestração / Graph: **LangChain** & **LangGraph**
- LLM: **Llama-3-8b** (via Groq Cloud)
- API: **FastAPI**
- Interface: **Streamlit**
- Banco Vetorial: **ChromaDB**
- Containerização: **Docker** & **Docker Compose**

---

## Estrutura do Repositório

```
agent-swarm/
├── app/
│   ├── agents.py        # Definição do Grafo, Router e prompts dos agentes
│   ├── database.py      # Banco de dados mockado (clientes, saldos, status)
│   ├── tools.py         # Ferramentas (busca web, RAG, get_profile)
│   ├── vector_store.py  # Lógica de conexão com ChromaDB
│   ├── main.py          # API Gateway (FastAPI)
│   └── frontend.py      # Interface visual (Streamlit)
├── chroma_db/           # Persistência do banco vetorial
├── ingest_data.py       # Script para popular o RAG (scraping)
├── Dockerfile           # Imagem otimizada (PyTorch CPU)
├── docker-compose.yml   # Orquestração dos serviços (backend + frontend)
└── requirements.txt     # Dependências
```

---

## Pré‑requisitos

- Docker e Docker Compose instalados.
- Chave de API da Groq (pode ser de teste).

---

## Como Executar

1. Clone o repositório:

```bash
git clone https://github.com/rafa-rez/cloudwalk-challenge.git
cd agent-swarm
```

2. Crie um arquivo `.env` na raiz com as variáveis necessárias:

```env
GROQ_MODEL=llama-3.1-8b-instant
CHAVE_GROQ=sua_chave_aqui
API_URL=http://backend:8000/api/chat
```

3. Suba os containers:

```bash
docker-compose up --build
```

4. Acesse a aplicação:

- Frontend (chat & testes): `http://localhost:8501`
- API Docs (Swagger): `http://localhost:8000/docs`

---

## Como Testar (QA)

No frontend há uma aba **Bateria de Testes** com cenários pré‑configurados que usam entradas do `app/database.py`:

- **Client Happy**: usuário com saldo positivo.
- **Client Blocked**: usuário com bloqueio por fraude (teste de segurança).
- **Client Debt**: usuário com saldo negativo.
- **Attacker**: simulação de jailbreak / prompt injection.

Clique em **Executar Bateria de Testes** para observar o roteamento, assertividade e métricas de latência em tempo real.

---

## Notas de Desenvolvimento

- **Ingestão de Dados**: Para atualizar o conhecimento do bot, edite as URLs em `ingest_data.py` e execute o script localmente ou dentro do container para repopular `chroma_db`.
- **Mock DB**: Adicione novos casos de teste editando `app/database.py`.
- **Roteiros de Segurança**: O fluxo de guardrails é composto por uma checagem inicial de palavras‑chave e prompts adicionais executados pelo Guardrail Agent; ajustes podem ser feitos em `app/agents.py` e `app/tools.py`.

