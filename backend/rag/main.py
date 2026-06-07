from rag.file_parsers.main import parse_file
from rag.text_chunking.main import text_chunking
from rag.vector_store.main import store_embeddings
from rag.hybrid_search.main import query_index

def rag_pipeline(file_path: str, file_type: str, query_text: str):
    # Step 1: Parse the file
    markdown_content = parse_file(file_path, file_type)

    # Step 2: Chunk the text
    chunks = text_chunking(markdown_content)

    # Step 3: Store embeddings in vector store
    stored  = store_embeddings(chunks)

    index_name = stored["index_name"]
    bm25_encoder = stored["bm25_encoder"]

    # Step 4: Query the index (example query)

    results = query_index(query_text, index_name=index_name, bm25_encoder=bm25_encoder)

    return results
