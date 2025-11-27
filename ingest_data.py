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

# Configuracao de Logging Corporativo
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("DataIngestion")

load_dotenv()

# --- Configuracoes e Constantes ---
CHROMA_PATH = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Headers para simular um navegador real e evitar bloqueios (403 Forbidden)
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
    Carrega documentos HTML das URLs fornecidas de forma resiliente.
    
    Tenta carregar cada URL individualmente para garantir que falhas em uma pagina
    nao impecam o carregamento das demais.

    Parameters:
    - urls (List[str]): Lista de URLs para processamento.

    Returns:
    - List[Document]: Lista de documentos LangChain carregados com sucesso.
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
            
            # Enriquece metadados se necessario e adiciona a lista principal
            for doc in docs:
                # Garante que a fonte esteja clara nos metadados
                if "source" not in doc.metadata:
                    doc.metadata["source"] = url
                documents.append(doc)
                
            logger.info(f"Sucesso ao carregar: {url}")
            
            # Breve pausa para nao sobrecarregar o servidor alvo (boas praticas de scraping)
            time.sleep(0.5) 
            
        except Exception as e:
            logger.error(f"Falha ao carregar URL {url}: {e}")
            continue

    logger.info(f"Carregamento concluido. Total de documentos brutos: {len(documents)}")
    return documents

def split_text(documents: List[Document]) -> List[Document]:
    """
    Divide os documentos em pedacos menores (chunks) para indexacao.

    Parameters:
    - documents (List[Document]): Lista de documentos originais.

    Returns:
    - List[Document]: Lista de chunks processados.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Documentos divididos em {len(chunks)} chunks de texto.")
    return chunks

def save_to_chroma(chunks: List[Document]):
    """
    Gera embeddings e persiste os chunks no banco vetorial ChromaDB.

    Parameters:
    - chunks (List[Document]): Lista de fragmentos de texto.
    """
    # Verifica se existem chunks antes de prosseguir
    if not chunks:
        logger.warning("Nenhum chunk disponivel para ingestao. Processo abortado.")
        return

    logger.info(f"Inicializando modelo de embeddings: {EMBEDDING_MODEL}")
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Opcional: Limpar banco anterior para evitar duplicatas em re-execucoes
    # shutil.rmtree(CHROMA_PATH, ignore_errors=True) 

    logger.info(f"Persistindo dados no diretorio: {CHROMA_PATH}")
    try:
        # Batch size padrao do Chroma e eficiente, mas o processo pode demorar dependendo da CPU
        Chroma.from_documents(
            documents=chunks,
            embedding=embedding_function,
            persist_directory=CHROMA_PATH
        )
        logger.info("Ingestao concluida e banco vetorial salvo com sucesso.")
        
    except Exception as e:
        logger.critical(f"Erro critico ao salvar no ChromaDB: {e}")
        raise e

def main():
    """Funcao orquestradora do pipeline de ingestao."""
    start_time = time.time()
    
    try:
        # 1. Carregar
        raw_docs = load_documents(TARGET_URLS)
        
        # 2. Dividir
        chunks = split_text(raw_docs)
        
        # 3. Indexar e Salvar
        save_to_chroma(chunks)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Processo finalizado em {elapsed_time:.2f} segundos.")
        
    except Exception as e:
        logger.critical(f"Falha na execucao do script de ingestao: {e}")

if __name__ == "__main__":
    main()