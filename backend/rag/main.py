from rag.file_parsers.main import parse_file
from rag.text_chunking.main import text_chunking
from rag.vector_store.main import generate_and_store_embeddings
from rag.hybrid_search.main import (
    query_index,
    format_retrieved_context,
    retrieve_with_sources,
)

INDEX_NAME = "multi-agent-corporate-index"


def ingest_document(
    file_path: str,
    file_type: str,
) -> dict:
    """
    Parse, chunk, embed, and store a document in Pinecone.

    Args:
        file_path (str):
            Path to the uploaded file.

        file_type (str):
            Supported file type (pdf, csv, xlsx, docx, etc.).

    Returns:
        dict:
            Pinecone ingestion summary.
    """

    # -------------------------------------------------------------
    # Parse
    # -------------------------------------------------------------

    documents = parse_file(
        file_path=file_path,
        file_type=file_type,
    )

    if not documents:
        raise ValueError(
            "No documents were produced by parser."
        )

    # -------------------------------------------------------------
    # Chunk
    # -------------------------------------------------------------

    chunks = text_chunking(
        documents=documents
    )

    if not chunks:
        raise ValueError(
            "No chunks were produced."
        )

    # -------------------------------------------------------------
    # Store
    # -------------------------------------------------------------

    result = generate_and_store_embeddings(
        chunks=chunks
    )

    return result


def retrieve_documents(
    query_text: str,
    top_k: int = 10,
    filter_dict: dict | None = None,
):
    """
    Retrieve relevant chunks from Pinecone.

    Args:
        query_text (str):
            User query.

        top_k (int):
            Number of chunks to retrieve.

        filter_dict (dict | None):
            Optional Pinecone metadata filter.

    Returns:
        QueryResponse
    """

    return query_index(
        query_text=query_text,
        index_name=INDEX_NAME,
        top_k=top_k,
        filter_dict=filter_dict,
    )


def retrieve_context(
    query_text: str,
    top_k: int = 10,
    filter_dict: dict | None = None,
) -> str:
    """
    Retrieve and format context for LLM prompting.

    Args:
        query_text (str):
            User query.

        top_k (int):
            Number of chunks.

        filter_dict (dict | None):
            Optional metadata filter.

    Returns:
        str
    """

    results = retrieve_documents(
        query_text=query_text,
        top_k=top_k,
        filter_dict=filter_dict,
    )

    return format_retrieved_context(
        results
    )


def retrieve_context_with_sources(
    query_text: str,
    top_k: int = 10,
    filter_dict: dict | None = None,
):
    """
    Retrieve context along with source metadata.

    Args:
        query_text (str):
            User query.

        top_k (int):
            Number of chunks.

        filter_dict (dict | None):
            Optional metadata filter.

    Returns:
        list[dict]
    """

    return retrieve_with_sources(
        query_text=query_text,
        index_name=INDEX_NAME,
        top_k=top_k,
        filter_dict=filter_dict,
    )


def rag_pipeline(
    file_path: str,
    file_type: str,
    query_text: str,
):
    """
    End-to-end pipeline for testing.

    WARNING:
    This re-indexes the document every time it runs.
    Prefer ingest_document() + retrieve_context()
    in production.

    Args:
        file_path (str):
            File to ingest.

        file_type (str):
            File type.

        query_text (str):
            User question.

    Returns:
        QueryResponse
    """

    ingestion_result = ingest_document(
        file_path=file_path,
        file_type=file_type,
    )

    results = query_index(
        query_text=query_text,
        index_name=ingestion_result["index_name"],
    )

    return results