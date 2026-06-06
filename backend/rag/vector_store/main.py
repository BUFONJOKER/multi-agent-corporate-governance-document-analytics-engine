import hashlib
import logging

from langchain_pinecone import PineconeVectorStore
from pinecone.exceptions import PineconeException

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
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
# Retryable Pinecone Upload
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
def upload_to_pinecone(
    chunks,
    cached_embedder,
    ids,
):
    """
    Upload documents to Pinecone.

    Retries only transient Pinecone/network failures.
    """

    logger.info(
        "Uploading %s documents to Pinecone index '%s'",
        len(chunks),
        INDEX_NAME,
    )

    return PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=cached_embedder,
        index_name=INDEX_NAME,
        ids=ids,
    )


# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------

def store_embeddings(
    chunks,
    cached_embedder,
):
    """
    Store document chunks in Pinecone.

    Returns:
        PineconeVectorStore

    Raises:
        ValueError
        RuntimeError
    """

    try:
        # ---------------------------------------------------------------------
        # Validation
        # ---------------------------------------------------------------------

        if not chunks:
            raise ValueError(
                "No chunks provided for Pinecone ingestion."
            )

        ids = []

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

            # -------------------------------------------------------------
            # Deterministic ID generation
            # -------------------------------------------------------------

            chunk_id = hashlib.sha256(
                chunk.page_content.encode("utf-8")
            ).hexdigest()

            ids.append(chunk_id)

        logger.info(
            "Generated %s Pinecone vector IDs",
            len(ids),
        )

        # ---------------------------------------------------------------------
        # Upload
        # ---------------------------------------------------------------------

        vector_store = upload_to_pinecone(
            chunks=chunks,
            cached_embedder=cached_embedder,
            ids=ids,
        )

        logger.info(
            "Successfully stored %s chunks in Pinecone",
            len(chunks),
        )

        return vector_store

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