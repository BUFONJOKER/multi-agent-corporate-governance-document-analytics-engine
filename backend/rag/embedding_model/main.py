from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def load_model():
    """Loads the OpenAI embedding model with specified dimensions."""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        dimensions=1024,
    )
