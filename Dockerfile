# Imagem base Python
FROM python:3.10-slim

WORKDIR /app

# Variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Instalação de bibliotecas Python pesadas (Cache Layer)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir sentence-transformers

# Instalação das dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cópia do código fonte e scripts
COPY . .

# Exposição de portas e permissões de execução
EXPOSE 8000
EXPOSE 8501
RUN chmod +x start.sh

# Entrypoint
CMD ["./start.sh"]