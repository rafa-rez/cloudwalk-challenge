# Imagem base
FROM python:3.10-slim

WORKDIR /app

# Variaveis de ambiente para otimizacao do Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalacao de dependencias do sistema (Adicionado graphviz aqui!)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# 1. Instalacao otimizada do PyTorch (Versao CPU para reduzir tamanho da imagem)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 2. Instalacao do Sentence Transformers (dependencia pesada)
RUN pip install --no-cache-dir sentence-transformers

# 3. Instalacao das demais dependencias do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia do codigo fonte
COPY . .

# Expõe as portas (API e Streamlit)
EXPOSE 8000
EXPOSE 8501

# O comando padrão continua sendo a API, mas será sobrescrito no compose para o frontend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]