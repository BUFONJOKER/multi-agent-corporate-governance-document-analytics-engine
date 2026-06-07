from typing import Optional

from pinecone import Pinecone

from config import PINECONE_API_KEY

from rag.embedding.main import (
    get_dense_embedder,
    get_bm25_encoder,
)


def query_index(
    query_text: str,
    index_name: str,
    top_k: int = 10,
    filter_dict: Optional[dict] = None,
):
    """
    Perform hybrid retrieval from Pinecone using dense embeddings
    and BM25 sparse vectors.

    Args:
        query_text (str):
            User query.

        index_name (str):
            Pinecone index name.

        top_k (int, optional):
            Number of results to return.

        filter_dict (dict, optional):
            Pinecone metadata filter.

    Returns:
        QueryResponse:
            Pinecone query response.
    """

    if not query_text:
        raise ValueError(
            "query_text cannot be empty."
        )

    query_text = query_text.strip()

    if not query_text:
        raise ValueError(
            "query_text cannot be blank."
        )

    # ------------------------------------------------------------------
    # Pinecone Connection
    # ------------------------------------------------------------------

    pc = Pinecone(
        api_key=PINECONE_API_KEY
    )

    index = pc.Index(index_name)

    # ------------------------------------------------------------------
    # Dense Query Embedding
    # ------------------------------------------------------------------

    dense_embedder = get_dense_embedder()

    query_dense = dense_embedder.embed_query(
        query_text
    )

    # ------------------------------------------------------------------
    # Sparse Query Embedding
    # ------------------------------------------------------------------

    bm25_encoder = get_bm25_encoder()

    query_sparse = bm25_encoder.encode_queries(
        query_text
    )

    if (
        isinstance(query_sparse, list)
        and len(query_sparse) > 0
    ):
        query_sparse = query_sparse[0]

    # ------------------------------------------------------------------
    # Hybrid Search
    # ------------------------------------------------------------------

    query_params = {
        "vector": query_dense,
        "sparse_values": query_sparse,
        "top_k": top_k,
        "include_metadata": True,
    }

    if filter_dict:
        query_params["filter"] = filter_dict

    results = index.query(
        **query_params
    )

    return results


def format_retrieved_context(
    query_results,
) -> str:
    """
    Convert Pinecone results into a single context string.

    Args:
        query_results:
            Pinecone query response.

    Returns:
        str:
            Concatenated context.
    """

    if (
        not query_results
        or not hasattr(query_results, "matches")
    ):
        return ""

    contexts = []

    for match in query_results.matches:

        metadata = (
            match.metadata
            if hasattr(match, "metadata")
            else {}
        )

        context = metadata.get(
            "context",
            "",
        )

        if context:
            contexts.append(context)

    return "\n\n".join(contexts)


def retrieve_context(
    query_text: str,
    index_name: str,
    top_k: int = 10,
    filter_dict: Optional[dict] = None,
) -> str:
    """
    Convenience wrapper that performs retrieval
    and returns formatted context.

    Args:
        query_text (str):
            User query.

        index_name (str):
            Pinecone index.

        top_k (int):
            Number of chunks to retrieve.

        filter_dict (dict, optional):
            Pinecone metadata filter.

    Returns:
        str:
            Retrieved context.
    """

    results = query_index(
        query_text=query_text,
        index_name=index_name,
        top_k=top_k,
        filter_dict=filter_dict,
    )

    return format_retrieved_context(
        results
    )


def retrieve_with_sources(
    query_text: str,
    index_name: str,
    top_k: int = 10,
    filter_dict: Optional[dict] = None,
):
    """
    Retrieve chunks along with metadata.

    Useful for citations and source tracking.

    Args:
        query_text (str):
            User query.

        index_name (str):
            Pinecone index.

        top_k (int):
            Number of chunks to retrieve.

        filter_dict (dict, optional):
            Pinecone metadata filter.

    Returns:
        list[dict]:
            Retrieved chunks and metadata.
    """

    results = query_index(
        query_text=query_text,
        index_name=index_name,
        top_k=top_k,
        filter_dict=filter_dict,
    )

    retrieved_chunks = []

    for match in results.matches:

        metadata = (
            match.metadata
            if hasattr(match, "metadata")
            else {}
        )

        retrieved_chunks.append(
            {
                "id": match.id,
                "score": match.score,
                "context": metadata.get(
                    "context",
                    "",
                ),
                "source": metadata.get(
                    "source",
                    "",
                ),
                "file_name": metadata.get(
                    "file_name",
                    "",
                ),
                "file_type": metadata.get(
                    "file_type",
                    "",
                ),
                "page": metadata.get(
                    "page",
                ),
                "row": metadata.get(
                    "row",
                ),
                "chunk_id": metadata.get(
                    "chunk_id",
                ),
            }
        )

    return retrieved_chunks