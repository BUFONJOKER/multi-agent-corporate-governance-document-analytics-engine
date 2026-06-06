from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


def load_model():
    """
    Load the OpenAI embedding model used throughout the RAG pipeline.

    We use the `text-embedding-3-small` model because it provides an excellent
    balance of quality, speed, and cost for retrieval-augmented generation (RAG)
    applications.

    Key characteristics:
    - Cost-effective compared to larger embedding models.
    - Suitable for semantic search, document retrieval, clustering,
      classification, and similarity matching tasks.
    - Supports configurable output dimensions.
    - Configured here to generate 1024-dimensional embeddings to match the
      Pinecone index configuration used by this application.
    - Delivers strong retrieval performance while helping reduce storage and
      vector database costs compared to higher-dimensional embeddings.

    Returns:
        OpenAIEmbeddings: Configured embedding model instance.
    """

    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        dimensions=1024,
    )
