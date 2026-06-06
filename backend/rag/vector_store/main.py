from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from config import PINECONE_API_KEY

import hashlib
# from langsmith import traceable

# @traceable
def store_embeddings(chunks, cached_embedder):
    """Store chunks and their cache-backed embeddings in Pinecone and return the vector store instance."""

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = 'multi-agent-corporate-index'

    # Generate unique IDs deterministically based on the text content itself
    ids = []
    for chunk in chunks:
        # Create a unique SHA-256 hash using the chunk's text
        text_hash = hashlib.sha256(chunk.page_content.encode('utf-8')).hexdigest()
        ids.append(text_hash)

    # Pass the explicit IDs list to LangChain
    vector_store = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=cached_embedder,
        index_name=index_name,
        ids=ids # 🧠 Pinecone will now overwrite duplicates instead of copying them!
    )

    return vector_store
