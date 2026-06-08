import hashlib
import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document

from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore

from pinecone_text.sparse import BM25Encoder

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

from rag.embedding_model.main import load_model


# =============================================================================
# Configuration
# =============================================================================

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1024

# Increment this when changing embedding model/chunking strategy
EMBEDDING_VERSION = "v1"

NAMESPACE = (
    f"{EMBEDDING_MODEL}:"
    f"{EMBEDDING_DIMENSIONS}:"
    f"{EMBEDDING_VERSION}"
)

# =============================================================================
# Cache Directories
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent

BACKEND_STORE_DIR = os.environ.get("BACKEND_STORE_DIR")

if BACKEND_STORE_DIR:
    CACHE_PATH = (
        Path(BACKEND_STORE_DIR)
        / "rag_embedding_cache"
    )
else:
    CACHE_PATH = (
        BASE_DIR.parent.parent
        / "rag_embedding_cache"
    )

CACHE_PATH.mkdir(
    parents=True,
    exist_ok=True,
)

BM25_PATH = CACHE_PATH / "bm25_values.json"


# =============================================================================
# Cache Helpers
# =============================================================================

def sha256_encoder_with_namespace(
    text: str,
) -> str:
    """
    Generate a deterministic cache key.
    """

    combined_input = (
        f"{NAMESPACE}{text}"
    )

    return hashlib.sha256(
        combined_input.encode("utf-8")
    ).hexdigest()


# =============================================================================
# Dense Embeddings
# =============================================================================

def get_dense_embedder():
    """
    Create cache-backed embedding model.
    """

    underlying_embeddings = load_model()

    store = LocalFileStore(
        str(CACHE_PATH)
    )

    cached_embedder = (
        CacheBackedEmbeddings.from_bytes_store(
            underlying_embeddings=underlying_embeddings,
            document_embedding_cache=store,
            key_encoder=sha256_encoder_with_namespace,
        )
    )

    return cached_embedder


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
    texts: List[str],
):
    """
    Generate embeddings with retries.
    """

    return cached_embedder.embed_documents(
        texts
    )


def generate_dense_embeddings(
    chunks: List[Document],
):
    """
    Generate dense embeddings for document chunks.

    Args:
        chunks (List[Document]):
            Chunked documents.

    Returns:
        List[List[float]]
    """

    if not chunks:
        return []

    texts = [
        chunk.page_content
        for chunk in chunks
        if chunk.page_content.strip()
    ]

    if not texts:
        return []

    cached_embedder = get_dense_embedder()

    dense_vectors = warmup_embeddings(
        cached_embedder,
        texts,
    )

    return dense_vectors


# =============================================================================
# BM25
# =============================================================================

def fit_bm25_encoder(
    chunks: List[Document],
):
    """
    Train and persist BM25 vocabulary.

    Run this when building a fresh index.
    """

    if not chunks:
        raise ValueError(
            "Cannot fit BM25 on empty chunk list."
        )

    texts = [
        chunk.page_content
        for chunk in chunks
        if chunk.page_content.strip()
    ]

    bm25 = BM25Encoder()

    bm25.fit(texts)

    bm25.dump(
        str(BM25_PATH)
    )

    return bm25


def get_bm25_encoder(fallback_chunks: List[Document] = None):
    """
    Load existing BM25 encoder. If missing, dynamically boots up
    a baseline file using the current chunks payload.
    """

    if not BM25_PATH.exists():
        if fallback_chunks:
            print(f"[*] BM25 cache missing at {BM25_PATH}. Fitting inline with current document batch...")
            return fit_bm25_encoder(fallback_chunks)

        # Absolute fallback layout with corporate domain keywords if zero chunks passed
        print(f"[*] BM25 cache missing and no chunks provided. Creating baseline fallback...")
        fallback_corpus = [
            Document(page_content="Corporate governance policy guidelines regulatory compliance risk framework."),
            Document(page_content="Board of directors executive audit committee financial oversight stakeholders."),
            Document(page_content="Document data analytics parsing retrieval augmented generation vector index engine.")
        ]
        return fit_bm25_encoder(fallback_corpus)

    return BM25Encoder().load(
        str(BM25_PATH)
    )


def generate_sparse_bm25(
    chunks: List[Document],
):
    """
    Generate sparse vectors using persisted BM25 vocabulary.

    Args:
        chunks (List[Document])

    Returns:
        List[dict]
    """

    if not chunks:
        return []

    bm25 = get_bm25_encoder(fallback_chunks=chunks)

    texts = [
        chunk.page_content
        for chunk in chunks
        if chunk.page_content.strip()
    ]

    sparse_vectors = bm25.encode_documents(
        texts
    )

    return sparse_vectors