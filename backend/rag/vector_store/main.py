import hashlib
import logging
from typing import List

from langchain_core.documents import Document

from pinecone import Pinecone
from pinecone.exceptions import PineconeException

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from config import PINECONE_API_KEY

from rag.embedding.main import (
    generate_dense_embeddings,
    generate_sparse_bm25,
)

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

INDEX_NAME = "multi-agent-corporate-index"


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def generate_and_store_embeddings(
    chunks: List[Document],
) -> dict:
    """
    Generate dense and sparse embeddings and store them in Pinecone.

    Args:
        chunks (List[Document]):
            Chunked LangChain documents.

    Returns:
        dict:
            Information about the ingestion process.
    """

    try:
        if not chunks:
            raise ValueError(
                "No chunks provided for Pinecone ingestion."
            )

        return upsert_to_pinecone(
            chunks=chunks,
            index_name=INDEX_NAME,
        )

    except ValueError:
        raise

    except PineconeException as e:
        logger.exception(
            "Pinecone operation failed."
        )

        raise RuntimeError(
            f"Pinecone upload failed: {str(e)}"
        ) from e

    except Exception as e:
        logger.exception(
            "Unexpected error while storing embeddings."
        )

        raise RuntimeError(
            f"Failed to store embeddings: {str(e)}"
        ) from e


# -----------------------------------------------------------------------------
# Pinecone Upsert
# -----------------------------------------------------------------------------

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
def upsert_to_pinecone(
    chunks: List[Document],
    index_name: str = INDEX_NAME,
) -> dict:
    """
    Upsert dense and sparse vectors into Pinecone.

    Args:
        chunks (List[Document]):
            Chunked LangChain documents.

        index_name (str):
            Pinecone index name.

    Returns:
        dict:
            Ingestion summary.
    """

    if not chunks:
        raise ValueError(
            "No chunks provided for Pinecone ingestion."
        )

    validated_chunks = []

    for idx, chunk in enumerate(chunks):

        if not hasattr(chunk, "page_content"):
            raise ValueError(
                f"Chunk at index {idx} is missing page_content."
            )

        if not isinstance(chunk.page_content, str):
            raise ValueError(
                f"Chunk at index {idx} page_content must be a string."
            )

        if not chunk.page_content.strip():
            raise ValueError(
                f"Chunk at index {idx} contains empty text."
            )

        if not hasattr(chunk, "metadata") or chunk.metadata is None:
            chunk.metadata = {}

        validated_chunks.append(chunk)

    logger.info(
        "Generating embeddings for %s chunks",
        len(validated_chunks),
    )

    # -------------------------------------------------------------------------
    # Dense Embeddings
    # -------------------------------------------------------------------------

    dense_vectors = generate_dense_embeddings(
        validated_chunks
    )

    # -------------------------------------------------------------------------
    # Sparse Embeddings (BM25)
    # -------------------------------------------------------------------------

    sparse_vectors, _ = generate_sparse_bm25(
        validated_chunks
    )

    if len(dense_vectors) != len(validated_chunks):
        raise RuntimeError(
            f"Dense vector count mismatch. "
            f"Expected {len(validated_chunks)}, "
            f"got {len(dense_vectors)}."
        )

    if len(sparse_vectors) != len(validated_chunks):
        raise RuntimeError(
            f"Sparse vector count mismatch. "
            f"Expected {len(validated_chunks)}, "
            f"got {len(sparse_vectors)}."
        )

    # -------------------------------------------------------------------------
    # Pinecone Connection
    # -------------------------------------------------------------------------

    pc = Pinecone(
        api_key=PINECONE_API_KEY
    )

    index = pc.Index(index_name)

    upsert_data = []
    upserted_ids = []

    # -------------------------------------------------------------------------
    # Build Pinecone Records
    # -------------------------------------------------------------------------

    for i, chunk in enumerate(validated_chunks):

        metadata = chunk.metadata or {}

        source = metadata.get("source", "")
        file_name = metadata.get("file_name", "")
        file_type = metadata.get("file_type", "")

        page = metadata.get("page")
        row = metadata.get("row")

        chunk_id = metadata.get(
            "chunk_id",
            i,
        )

        # Create collision-resistant unique ID

        unique_string = (
            f"{source}|"
            f"{page}|"
            f"{row}|"
            f"{chunk_id}|"
            f"{chunk.page_content}"
        )

        doc_id = hashlib.sha256(
            unique_string.encode("utf-8")
        ).hexdigest()

        pinecone_metadata = {
            "context": chunk.page_content,
            "source": str(source),
            "file_name": str(file_name),
            "file_type": str(file_type),
            "page": page,
            "row": row,
            "chunk_id": chunk_id,
            "chunk_size": metadata.get(
                "chunk_size",
                len(chunk.page_content),
            ),
        }

        # Remove None values

        pinecone_metadata = {
            k: v
            for k, v in pinecone_metadata.items()
            if v is not None
        }

        upsert_data.append(
            {
                "id": doc_id,
                "values": dense_vectors[i],
                "sparse_values": sparse_vectors[i],
                "metadata": pinecone_metadata,
            }
        )

        upserted_ids.append(doc_id)

    # -------------------------------------------------------------------------
    # Upsert
    # -------------------------------------------------------------------------

    index.upsert(
        vectors=upsert_data
    )

    logger.info(
        "Successfully upserted %s vectors into '%s'",
        len(upsert_data),
        index_name,
    )

    return {
        "index_name": index_name,
        "upserted_count": len(upsert_data),
        "ids": upserted_ids,
    }