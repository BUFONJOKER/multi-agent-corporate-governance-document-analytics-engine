from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def text_chunking(
    documents: List[Document],
    chunk_size: int = 512,
    chunk_overlap: int = 30,
) -> List[Document]:
    """
    Split LangChain documents into smaller chunks while preserving metadata.

    This function works with documents parsed from PDFs, CSVs, Excel files,
    DOCX files, TXT files, and other supported formats.

    Args:
        documents (List[Document]):
            List of LangChain Document objects.

        chunk_size (int, optional):
            Maximum size of each chunk. Defaults to 512.

        chunk_overlap (int, optional):
            Number of overlapping characters between chunks.
            Defaults to 30.

    Returns:
        List[Document]:
            Chunked documents with original metadata preserved and
            additional chunk metadata added.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = text_splitter.split_documents(documents)

    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = idx
        chunk.metadata["chunk_size"] = len(chunk.page_content)

    return chunks