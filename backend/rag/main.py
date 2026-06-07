from rag.file_parsers.main import parse_file
from rag.text_chunking.main import text_chunking
from rag.vector_store.main import generate_and_store_embeddings
from rag.hybrid_search.main import query_index


def rag_pipeline(file_path: str, file_type: str, query_text: str):
    """
    Execute the complete Retrieval-Augmented Generation (RAG) pipeline.

    This function orchestrates the end-to-end document processing workflow:
    1. Parses the uploaded file into markdown/text format.
    2. Splits the parsed content into smaller chunks suitable for retrieval.
    3. Generates dense and sparse embeddings for each chunk and stores them
       in the configured vector database.
    4. Executes a hybrid search query against the vector store using the
       provided query text.
    5. Returns the retrieved search results.

    Args:
        file_path (str):
            Absolute or relative path to the input document that will be
            processed by the RAG pipeline.

        file_type (str):
            Type of the input file. Examples include:
            - "pdf"
            - "csv"

            The value determines which parser will be used to extract content.

        query_text (str):
            User query or search question used to retrieve the most relevant
            document chunks from the vector store.

    Returns:
        QueryResponse:
            Pinecone query response containing the most relevant retrieved
            document chunks, similarity scores, vector IDs, and metadata
            associated with the matched records.

    Raises:
        FileNotFoundError:
            If the specified file does not exist.

        ValueError:
            If the file type is unsupported or invalid input data is provided.

        RuntimeError:
            If parsing, chunking, embedding generation, vector storage,
            or retrieval operations fail.

    Example:
        >>> results = rag_pipeline(
        ...     file_path="data/annual_report.pdf",
        ...     file_type="pdf",
        ...     query_text="What are the company's revenue growth projections?"
        ... )
        >>> print(results)
    """

    # Step 1: Parse the file
    markdown_content = parse_file(file_path, file_type)

    # Step 2: Chunk the text
    chunks = text_chunking(markdown_content)

    # Step 3: Store embeddings in vector store
    stored = generate_and_store_embeddings(chunks)

    index_name = stored["index_name"]
    bm25_encoder = stored["bm25_encoder"]

    # Step 4: Query the index
    results = query_index(
        query_text,
        index_name=index_name,
        bm25_encoder=bm25_encoder
    )

    return results