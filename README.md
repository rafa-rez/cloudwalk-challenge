# ⚡ CloudWalk Agent Swarm

**Uma arquitetura multi-agente robusta e modular para atendimento
financeiro inteligente.**\
Este projeto implementa um "Enxame de Agentes" (Agent Swarm) capaz de
orquestrar atendimentos complexos, separar responsabilidades e garantir
segurança através de Guardrails rígidos.

------------------------------------------------------------------------

## 🧠 Arquitetura do Sistema

O sistema utiliza **LangGraph** para gerenciar o fluxo de estado. A
decisão de roteamento é **Stateless** (focada na intenção imediata),
enquanto a experiência do usuário é **Stateful** (memória de conversa).

### 🧠 Arquitetura Stateful

<a href="./assets/arquitetura-statefull.svg">
  <img src="./assets/arquitetura-statefull.svg" width="400"/>
</a>

### 🧊 Arquitetura Stateless

<a href="./assets/arquitetura-stateless.svg">
  <img src="./assets/arquitetura-stateless.svg" width="400"/>
</a>

------------------------------------------------------------------------

## ✨ Funcionalidades Principais

### 1. Roteamento Inteligente & Stateless

O Router Agent analisa cada mensagem isoladamente. Ele não se deixa
enviesar pelo passado para decidir o destino, garantindo que uma mudança
brusca de assunto (ex: de "Erro no Pix" para "Quanto custa o Bitcoin?")
seja tratada corretamente.

### 2. Agentes Especializados

-   📚 **Knowledge Agent:** Utiliza RAG (Retrieval-Augmented Generation)
    com ChromaDB para responder sobre produtos InfinitePay e DuckDuckGo
    para buscas na web em tempo real.
-   🛠️ **Support Agent:** Conecta-se a um banco de dados (Mock) para
    realizar consultas sensíveis (Saldo, Status da Conta, Bloqueios).
-   🛡️ **Guardrail:** Camada de segurança determinística. Bloqueia
    tentativas de jailbreak, prompt injection ou linguagem tóxica.

### 3. Personalidade & Editoração

Um agente final (Personality) atua como editor de texto, garantindo tom
de voz da marca e formatação correta.\
Respostas vindas de Guardrail e Fallback **pulam** essa etapa.

### 4. Frontend Modular (Streamlit)

Interface dividida em abas estratégicas:

-   🧩 Chat Stateless (com grafo em tempo real)
-   💬 Chat Stateful (experiência tipo WhatsApp)
-   🧪 Bateria de Testes (QA automatizado)

------------------------------------------------------------------------

## 📂 Estrutura do Projeto

    app/
    ├── agents/
    │   ├── knowledge/
    │   ├── router/
    │   ├── support/
    │   └── utils/
    ├── core/
    │   ├── config.py
    │   ├── database.py
    │   ├── state.py
    │   ├── vector_store.py
    │   └── workflow.py
    ├── frontend/
    │   ├── components/
    │   ├── main.py
    │   └── styles.py
    └── main.py

------------------------------------------------------------------------

## 🚀 Como Executar

### Pré-requisitos

-   Docker & Docker Compose\
-   Uma chave de API da Groq Cloud (`GROQ_API_KEY`)

### 1. Criar `.env`

    CHAVE_GROQ=gsk_sua_chave_aqui...
    GROQ_MODEL=llama-3.1-8b-instant
    API_URL=http://backend:8000/api/chat

### 2. Executar com Docker

    docker-compose up --build

Acesse:\
Frontend → http://localhost:8501\
API Docs → http://localhost:8000/docs

### 3. Executar Testes

Na aba **🧪 Bateria de Testes** no Streamlit.

------------------------------------------------------------------------

## 🛠️ Detalhes Técnicos

### 🔍 Pipeline RAG

-   Scraping via `ingest_data.py`
-   Embeddings com `all-MiniLM-L6-v2`
-   ChromaDB busca top-4 chunks
-   Citação obrigatória de `metadata['source']`

### 🛡️ Guardrails

-   *Keyword Blocking*
-   *Sanitização de Saída*
-   *Isolamento de Memória*

------------------------------------------------------------------------

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-FF6F00?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)
