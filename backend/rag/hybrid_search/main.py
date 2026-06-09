from typing import Optional

# REMOVED global heavy imports to drop import latency down to 0ms
from config import PINECONE_API_KEY


# ------------------------------------------------------------------
# Pinecone Lazy Connection Helper
# ------------------------------------------------------------------
_index_instance = None

def _get_pinecone_index(index_name: str):
    """
    Establish a connection to your index lazily on the first query invocation.
    """
    global _index_instance
    if _index_instance is None:
        from pinecone import Pinecone

        pc = Pinecone(api_key=PINECONE_API_KEY)
        _index_instance = pc.Index(index_name)
    return _index_instance


# ------------------------------------------------------------------
# Core Retrieval Operations
# ------------------------------------------------------------------

def query_index(
    query_text: str,
    index_name: str,
    top_k: int = 10,
    filter_dict: Optional[dict] = None,
):
    """
    Perform hybrid retrieval from Pinecone using dense embeddings
    and BM25 sparse vectors.
    """

    if not query_text:
        raise ValueError("query_text cannot be empty.")

    query_text = query_text.strip()

    if not query_text:
        raise ValueError("query_text cannot be blank.")

    # 1. Grab index instance via our lazy network runner
    index = _get_pinecone_index(index_name)

    # ------------------------------------------------------------------
    # Dense Query Embedding (Inline Import)
    # ------------------------------------------------------------------
    from rag.embedding.main import get_dense_embedder

    dense_embedder = get_dense_embedder()
    query_dense = dense_embedder.embed_query(query_text)

    # ------------------------------------------------------------------
    # Sparse Query Embedding (Inline Import)
    # ------------------------------------------------------------------
    from rag.embedding.main import get_bm25_encoder

    bm25_encoder = get_bm25_encoder()
    query_sparse = bm25_encoder.encode_queries(query_text)

    if isinstance(query_sparse, list) and len(query_sparse) > 0:
        query_sparse = query_sparse[0]

    # ------------------------------------------------------------------
    # Hybrid Search Execution
    # ------------------------------------------------------------------
    query_params = {
        "vector": query_dense,
        "sparse_values": query_sparse,
        "top_k": top_k,
        "include_metadata": True,
    }

    if filter_dict:
        query_params["filter"] = filter_dict

    results = index.query(**query_params)

    return results





def retrieve_with_sources(
    query_text: str,
    index_name: str,
    top_k: int = 10,
    filter_dict: Optional[dict] = None,
):
    """
    Retrieve chunks along with metadata. Useful for citations and source tracking.
    """
    results = query_index(
        query_text=query_text,
        index_name=index_name,
        top_k=top_k,
        filter_dict=filter_dict,
    )

    retrieved_chunks = []

    for match in results.matches:
        metadata = match.metadata if hasattr(match, "metadata") else {}

        retrieved_chunks.append(
            {
                "id": match.id,
                "score": match.score,
                "context": metadata.get("context", ""),
                "source": metadata.get("source", ""),
                "file_name": metadata.get("file_name", ""),
                "file_type": metadata.get("file_type", ""),
                "page": metadata.get("page"),
                "row": metadata.get("row"),
                "chunk_id": metadata.get("chunk_id"),
            }
        )

    return retrieved_chunks