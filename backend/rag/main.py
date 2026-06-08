from typing import Union, List
from collections import defaultdict

from rag.file_parsers.main import parse_file
from rag.text_chunking.main import text_chunking
from rag.vector_store.main import generate_and_store_embeddings
from rag.detect_file_type.main import detect_file_type
from rag.hybrid_search.main import query_index, format_retrieved_context, retrieve_with_sources
from langchain_core.documents import Document

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
    top_k: int = 20,
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
    top_k: int = 20,
    top_n: int = 5,
    filter_dict: dict | None = None,
) -> str:
    """
    Retrieve, rerank, and format context for LLM prompting.

    Args:
        query_text (str):
            User query.

        top_k (int):
            Number of chunks.

        top_n (int):
            Number of top-ranked chunks to return.

        filter_dict (dict | None):
            Optional metadata filter.

    Returns:
        str
    """

    initial_results = retrieve_documents(
        query_text=query_text,
        top_k=top_k,
        filter_dict=filter_dict,
    )

    if not initial_results:
        return ""

    langchain_docs = []
    for match in initial_results.matches:
        doc = Document(
            page_content=match.metadata.get("context", ""),
            metadata={
                "source": match.metadata.get("source", ""),
                "score": match.score,
            },
        )
        langchain_docs.append(doc)

    from rag.rerank_model.main import load_reranker
    reranker = load_reranker()

    reranked_docs = reranker.compress_documents(documents=langchain_docs, query=query_text)

    return format_retrieved_context(
        reranked_docs[:top_n]
    )


def retrieve_context_with_sources(
    query_text: str,
    top_k: int = 20,
    top_n: int = 5,
    filter_dict: dict | None = None,
):
    """
    Retrieve, rerank, and format context along with source metadata.

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

    raw_response = retrieve_with_sources(
        query_text=query_text,
        index_name=INDEX_NAME,
        top_k=top_k,
        filter_dict=filter_dict,
    )

    matches = raw_response.get("matches", []) if isinstance(raw_response, dict) else raw_response.matches

    if not matches:
        return []

    langchain_docs = []
    for idx, match in enumerate(matches):
        metadata = match.get("metadata", {})
        text_content = metadata.get("context", "")

        # Track the entry index inside temporary metadata to re-sort original blocks seamlessly
        metadata["__temp_idx"] = idx

        langchain_docs.append(
            Document(page_content=text_content, metadata=metadata)
        )
    from rag.rerank_model.main import load_reranker
    reranker = load_reranker()

    reranked_docs = reranker.compress_documents(documents=langchain_docs, query=query_text)
    final_docs = reranked_docs[:top_n]

    # Map back items into your native dictionary layout based on new score priorities
    sorted_results = []
    for doc in final_docs:
        original_position = doc.metadata["__temp_idx"]
        matched_item = matches[original_position]

        # Update matching item score with the new Cohere relevance score
        if "relevance_score" in doc.metadata:
            matched_item["score"] = doc.metadata["relevance_score"]

        sorted_results.append(matched_item)

    return sorted_results


def rag_pipeline(
    file_path: Union[str, List[str]],
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

    ingestion_result = ingest_document(file_path=file_path)

    results = query_index(
        query_text=query_text,
        index_name=ingestion_result["index_name"],
    )

    return results