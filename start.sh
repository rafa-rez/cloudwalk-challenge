#!/bin/bash

# Verifica a existência e integridade do banco vetorial
if [ ! -d "chroma_db" ] || [ -z "$(ls -A chroma_db)" ]; then
    echo "📦 Banco Vetorial não detectado. Iniciando processo de ingestão..."
    python ingest_data.py
else
    echo "✅ Banco Vetorial detectado. Pulando etapa de ingestão."
fi

# Inicialização do servidor da API
echo "🚀 Iniciando servidor Uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port 8000