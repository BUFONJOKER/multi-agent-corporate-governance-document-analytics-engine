

_cached_reranker = None

def load_reranker():
    """
    Load the Cohere reranker model used in the RAG pipeline.
    Uses a lazy-loading singleton pattern to keep imports instant.
    """

    global _cached_reranker
    if _cached_reranker is None:

        from langchain_cohere import CohereRerank
        from dotenv import load_dotenv

        load_dotenv()

        reranker = CohereRerank(model="rerank-v4.0-fast")

        _cached_reranker = reranker

    return _cached_reranker