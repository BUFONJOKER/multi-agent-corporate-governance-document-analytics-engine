from typing import Union, List
from collections import defaultdict

from rag.file_parsers.main import parse_file
from rag.text_chunking.main import text_chunking
from rag.vector_store.main import generate_and_store_embeddings
from rag.detect_file_type.main import detect_file_type
from rag.hybrid_search.main import query_index, format_retrieved_context, retrieve_with_sources
INDEX_NAME = "multi-agent-corporate-index"

def ingest_document(
    file_path: Union[str, List[str]],
) -> dict:
    """
    Ingest single or multiple files into RAG system.
    File type is auto-detected.
    """

    # ----------------------------
    # Normalize input
    # ----------------------------

    if isinstance(file_path, str):
        file_path = [file_path]

    # ----------------------------
    # Group by file type
    # ----------------------------

    grouped = defaultdict(list)

    for fp in file_path:
        ft = detect_file_type(fp)
        grouped[ft].append(fp)

    # ----------------------------
    # Parse all files
    # ----------------------------

    all_docs = []

    for file_type, files in grouped.items():

        docs = parse_file(
            file_path=files,
            file_type=file_type,
        )

        if not docs:
            raise ValueError(
                f"No documents parsed for {file_type}"
            )

        all_docs.extend(docs)

    # ----------------------------
    # Chunk
    # ----------------------------

    chunks = text_chunking(all_docs)

    if not chunks:
        raise ValueError("No chunks created")

    # ----------------------------
    # Embed + Store
    # ----------------------------

    return generate_and_store_embeddings(chunks)


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
    file_path: Union[str, List[str]],
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
        file_path (Union[str, List[str]]):
            File or files to ingest.

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