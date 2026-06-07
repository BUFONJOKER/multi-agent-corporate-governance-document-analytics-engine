import hashlib
import logging
import os

from pinecone import Pinecone
from pinecone.exceptions import PineconeException

from rag.embedding.main import (
    generate_dense_embeddings,
    generate_sparse_bm25,
)

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from config import PINECONE_API_KEY
# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

INDEX_NAME = "multi-agent-corporate-index"



# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------


def generate_and_store_embeddings(chunks:list):
    """
    Store document chunks in Pinecone using hybrid upsert.

    This keeps the existing signature for backward compatibility, but now
    writes both dense and sparse vectors.

    Returns:
        dict

    Raises:
        ValueError
        RuntimeError
    """

    try:
        # ---------------------------------------------------------------------
        # Validation
        # ---------------------------------------------------------------------

        if not chunks:
            raise ValueError("No chunks provided for Pinecone ingestion.")


        return upsert_to_pinecone(
            chunks=chunks,
            index_name=INDEX_NAME,
        )

    except ValueError:
        raise

    except PineconeException as e:
        logger.exception("Pinecone operation failed.")

        raise RuntimeError(f"Pinecone upload failed: {str(e)}") from e

    except Exception as e:
        logger.exception("Unexpected error while storing embeddings.")

        raise RuntimeError(f"Failed to store embeddings: {str(e)}") from e


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(
        multiplier=1,
        min=2,
        max=30,
    ),
    retry=retry_if_exception_type(
        (
            PineconeException,
            ConnectionError,
            TimeoutError,
        )
    ),
    before_sleep=before_sleep_log(
        logger,
        logging.WARNING,
    ),
    reraise=True,
)
def upsert_to_pinecone(chunks: list, index_name: str = INDEX_NAME) -> dict:
    """Upsert dense + sparse vectors into Pinecone for hybrid search."""

    if not chunks:
        raise ValueError("No chunks provided for Pinecone ingestion.")

    validated_chunks = []

    for idx, chunk in enumerate(chunks):
        if not hasattr(chunk, "page_content"):
            raise ValueError(f"Chunk at index {idx} is missing page_content.")

        if not isinstance(chunk.page_content, str):
            raise ValueError(f"Chunk at index {idx} page_content must be a string.")

        if not chunk.page_content.strip():
            raise ValueError(f"Chunk at index {idx} contains empty text.")

        if not hasattr(chunk, "metadata") or chunk.metadata is None:
            chunk.metadata = {}

        validated_chunks.append(chunk)

    # 1. Get separate vectors
    logger.info(
        "Generating dense and sparse vectors for %s chunks", len(validated_chunks)
    )
    dense_vectors = generate_dense_embeddings(validated_chunks)
    sparse_vectors, bm25_encoder = generate_sparse_bm25(validated_chunks)

    if len(dense_vectors) != len(validated_chunks):
        raise RuntimeError(
            "Dense vector count mismatch. "
            f"Expected {len(validated_chunks)}, got {len(dense_vectors)}."
        )

    if len(sparse_vectors) != len(validated_chunks):
        raise RuntimeError(
            "Sparse vector count mismatch. "
            f"Expected {len(validated_chunks)}, got {len(sparse_vectors)}."
        )

    # 2. Connect to Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(index_name)

    upsert_data = []
    upserted_ids = []

    # 3. Zip everything together manually
    for i, chunk in enumerate(validated_chunks):
        # Create a unique ID or use one from chunk metadata
        doc_id = chunk.metadata.get("id")
        if not doc_id:
            doc_id = hashlib.sha256(chunk.page_content.encode("utf-8")).hexdigest()

        # Ensure values are primitives for metadata serialization.
        metadata = {
            str(k): (
                v if isinstance(v, (str, int, float, bool, type(None))) else str(v)
            )
            for k, v in chunk.metadata.items()
        }

        upsert_data.append(
            {
                "id": doc_id,
                "values": dense_vectors[i],  # Dense vector list
                "sparse_values": sparse_vectors[i],  # Sparse vector dict
                "metadata": {
                    "context": chunk.page_content,  # Store original text
                    **metadata,
                },
            }
        )
        upserted_ids.append(doc_id)

    # 4. Upsert to your index
    index.upsert(vectors=upsert_data)

    logger.info(
        "Successfully upserted %s vectors into index '%s'",
        len(upsert_data),
        index_name,
    )

    return {
        "index_name": index_name,
        "upserted_count": len(upsert_data),
        "ids": upserted_ids,
        "bm25_encoder": bm25_encoder
    }
