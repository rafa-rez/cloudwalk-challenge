import os
import logging
import time
from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("DataIngestion")

load_dotenv()

# Constantes de Configuração
CHROMA_PATH = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Headers para simulação de User-Agent
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

TARGET_URLS = [
    "https://www.infinitepay.io",
    "https://www.infinitepay.io/maquininha",
    "https://www.infinitepay.io/maquininha-celular",
    "https://www.infinitepay.io/tap-to-pay",
    "https://www.infinitepay.io/pdv",
    "https://www.infinitepay.io/receba-na-hora",
    "https://www.infinitepay.io/gestao-de-cobranca",
    "https://www.infinitepay.io/link-de-pagamento",
    "https://www.infinitepay.io/loja-online",
    "https://www.infinitepay.io/boleto",
    "https://www.infinitepay.io/conta-pj",
    "https://www.infinitepay.io/pix",
    "https://www.infinitepay.io/emprestimo",
    "https://www.infinitepay.io/cartao",
    "https://www.infinitepay.io/rendimento"
]

def load_documents(urls: List[str]) -> List[Document]:
    """
    Carrega documentos HTML a partir de uma lista de URLs com tratamento de exceções.
    
    Args:
        urls (List[str]): Lista de URLs alvo para scraping.

    Returns:
        List[Document]: Lista de documentos carregados e enriquecidos com metadados.
    """
    documents = []
    logger.info(f"Iniciando carregamento de {len(urls)} URLs...")

    for url in urls:
        try:
            loader = WebBaseLoader(
                web_paths=(url,), 
                header_template=REQUEST_HEADERS
            )
            docs = loader.load()
            
            for doc in docs:
                if "source" not in doc.metadata:
                    doc.metadata["source"] = url
                documents.append(doc)
                
            logger.info(f"Sucesso ao carregar: {url}")
            time.sleep(0.5) 
            
        except Exception as e:
            logger.error(f"Falha ao carregar URL {url}: {e}")
            continue

    logger.info(f"Carregamento concluído. Documentos brutos: {len(documents)}")
    return documents

def split_text(documents: List[Document]) -> List[Document]:
    """
    Divide documentos brutos em fragmentos (chunks) para otimização de embeddings.

    Args:
        documents (List[Document]): Lista de documentos originais.

    Returns:
        List[Document]: Lista de fragmentos processados.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Documentos divididos em {len(chunks)} chunks.")
    return chunks

def save_to_chroma(chunks: List[Document]):
    """
    Gera embeddings e persiste os dados no ChromaDB.

    Args:
        chunks (List[Document]): Fragmentos de texto para indexação.
    """
    if not chunks:
        logger.warning("Nenhum dado para ingestão.")
        return

    logger.info(f"Inicializando modelo de embeddings: {EMBEDDING_MODEL}")
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    logger.info(f"Persistindo dados em: {CHROMA_PATH}")
    try:
        Chroma.from_documents(
            documents=chunks,
            embedding=embedding_function,
            persist_directory=CHROMA_PATH
        )
        logger.info("Banco vetorial atualizado com sucesso.")
        
    except Exception as e:
        logger.critical(f"Erro ao salvar no ChromaDB: {e}")
        raise e

def main():
    """Orquestrador do pipeline de ingestão de dados."""
    start_time = time.time()
    
    try:
        raw_docs = load_documents(TARGET_URLS)
        chunks = split_text(raw_docs)
        save_to_chroma(chunks)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Pipeline finalizado em {elapsed_time:.2f} segundos.")
        
    except Exception as e:
        logger.critical(f"Falha na execução do pipeline: {e}")

if __name__ == "__main__":
    main()