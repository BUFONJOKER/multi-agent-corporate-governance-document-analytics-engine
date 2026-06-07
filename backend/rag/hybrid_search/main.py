from pinecone import Pinecone
from rag.embedding.main import get_dense_embedder

def query_index(query_text: str, index_name: str, bm25_encoder, mode="hybrid"):
    pc = Pinecone(api_key="YOUR_PINECONE_API_KEY")
    index = pc.Index(index_name)

    # Generate query vectors separately
    # Dense
    dense_embedder = get_dense_embedder() # retrieves cached setup
    query_dense = dense_embedder.embed_query(query_text)

    # Sparse
    query_sparse = bm25_encoder.encode_queries(query_text)

    # Execute search based on your needs
    if mode == "sparse_only":
        results = index.query(top_k=5, sparse_values=query_sparse, include_metadata=True)
    elif mode == "dense_only":
        results = index.query(top_k=5, vector=query_dense, include_metadata=True)
    else: # Hybrid
        results = index.query(
            top_k=5,
            vector=query_dense,
            sparse_values=query_sparse,
            include_metadata=True
        )

    return results