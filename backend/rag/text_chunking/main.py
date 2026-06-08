from typing import List
from langchain_core.documents import Document

# REMOVED: from langchain_text_splitters import RecursiveCharacterTextSplitter

def text_chunking(
    documents: List[Document],
    chunk_size: int = 512,
    chunk_overlap: int = 30,
) -> List[Document]:
    """
    Split LangChain documents into smaller chunks while preserving metadata.
    """
    # INLINE IMPORT: Moved inside to eliminate the 4.39-second import delay!
    from langchain_text_splitters import RecursiveCharacterTextSplitter

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