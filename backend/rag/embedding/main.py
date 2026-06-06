from langchain_openai import OpenAIEmbeddings
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore
import hashlib
import os
from pathlib import Path
# from langsmith import traceable

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


# @traceable
def generate_embeddings_for_chunks(chunks: list):
    """Generates cache-backed embeddings matching your 1024-dimension Pinecone Index and returns the embedder instance for use in LangChain's vector store."""

    text_to_embed = [chunk.page_content for chunk in chunks]

    # Keep dimensions explicit so they always match Pinecone index configuration.
    underlying_embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIMENSIONS,
    )

    store = LocalFileStore(str(CACHE_PATH))


    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=underlying_embeddings,
        document_embedding_cache=store,
        key_encoder=sha256_encoder_with_namespace,
    )

    # Triggering the actual embedding matrix calculation for caching purposes
    embeddings = cached_embedder.embed_documents(text_to_embed)

    # Return the cached_embedder instance so LangChain's vector store can use its methods
    return cached_embedder