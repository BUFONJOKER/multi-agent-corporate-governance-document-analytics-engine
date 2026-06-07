from pinecone import Pinecone
from rag.embedding.main import get_dense_embedder
from config import PINECONE_API_KEY

def query_index(query_text: str, index_name: str, bm25_encoder):
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(index_name)

    dense_embedder = get_dense_embedder()
    query_dense = dense_embedder.embed_query(query_text)

    query_sparse = bm25_encoder.encode_queries(query_text)

    # If your encoder returns a list of queries (e.g. pinecone-text can do this),
    # extract the first dictionary element:
    if isinstance(query_sparse, list) and len(query_sparse) > 0:
        query_sparse = query_sparse[0]

    return index.query(
        top_k=10,
        vector=query_dense,
        sparse_values=query_sparse,
        include_metadata=True,
        )
