from typing import List, Union

# Keep a global hidden tracker set to None
_cached_embeddings = None

def load_model():
    """
    Load the OpenAI embedding model used throughout the RAG pipeline.
    Uses a lazy-loading singleton pattern to keep imports instant.
    """
    global _cached_embeddings

    if _cached_embeddings is None:
        # Inline imports and initializations happen ONLY when load_model() is called
        from langchain_openai import OpenAIEmbeddings
        from dotenv import load_dotenv

        load_dotenv()

        _cached_embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1024,
        )

    return _cached_embeddings