from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore
import hashlib
import os
from pathlib import Path
# from langsmith import traceable
from rag.embedding_model.main import load_model
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from openai import (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
)
from pinecone_text.sparse import BM25Encoder


EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1024
NAMESPACE = f"{EMBEDDING_MODEL}:{EMBEDDING_DIMENSIONS}"
# Establish project baseline directory anchor
BASE_DIR = Path(__file__).resolve().parent

# Force paths to evaluate directly from an environment variable or absolute local fallback
BACKEND_STORE_DIR = os.environ.get("BACKEND_STORE_DIR")

if BACKEND_STORE_DIR:
    CACHE_PATH = Path(BACKEND_STORE_DIR) / "rag_embedding_cache"
else:
    # Traverses upward safely to locate the designated 'backend' directory structure
    # This ensures consistency during local terminal execution or multi-node worker tasks
    CACHE_PATH = BASE_DIR.parent.parent / "rag_embedding_cache"

# Create the folder structure automatically if it doesn't exist yet to prevent initialization errors
CACHE_PATH.mkdir(parents=True, exist_ok=True)


def sha256_encoder_with_namespace(text: str) -> str:
    combined_input = f"{NAMESPACE}{text}"
    return hashlib.sha256(combined_input.encode("utf-8")).hexdigest()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(
        multiplier=1,
        min=2,
        max=30,
    ),
    retry=retry_if_exception_type(
        (
            APIConnectionError,
            APITimeoutError,
            RateLimitError,
        )
    ),
    reraise=True,
)
def warmup_embeddings(
    cached_embedder,
    text_to_embed,
):
    return cached_embedder.embed_documents(text_to_embed)

def get_dense_embedder():
    '''
    Initializes and returns the cache-backed embedding model instance.
    '''
    underlying_embeddings = load_model()
    store = LocalFileStore(str(CACHE_PATH))

    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=underlying_embeddings,
        document_embedding_cache=store,
        key_encoder=sha256_encoder_with_namespace,
    )
    return cached_embedder


def generate_dense_embeddings(chunks: list):
    '''
    Generate dense embeddings for a list of text chunks.
    '''
    if not chunks:
        return []

    text_to_embed = [chunk.page_content for chunk in chunks]

    # Reuse the new initialization function
    cached_embedder = get_dense_embedder()

    dense_vectors = warmup_embeddings(cached_embedder, text_to_embed)
    return dense_vectors

def generate_sparse_bm25(chunks: list):
    """Generates BM25 sparse vectors separately."""
    text_to_embed = [chunk.page_content for chunk in chunks]

    bm25 = BM25Encoder()
    bm25.fit(text_to_embed)

    # Save parameters to use exactly the same vocabulary weightings during queries
    # bm25.dump("bm25_values.json")

    sparse_vectors = bm25.encode_documents(text_to_embed)
    return sparse_vectors, bm25