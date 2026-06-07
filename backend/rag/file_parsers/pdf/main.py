import os
from typing import List

from langchain_core.document_loaders import Blob
from langchain_core.documents import Document
from langchain_community.document_loaders.parsers.pdf import PyMuPDFParser


def pdf_parser(file_path: str) -> List[Document]:
    """
    Parse a single PDF file into LangChain Document objects.

    Args:
        file_path (str):
            Path to the PDF file.

    Returns:
        List[Document]:
            A list of LangChain Document objects, one per page (or parser chunk),
            with additional metadata including:
            - source: original file path
            - file_name: PDF file name
    """
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    blob = Blob.from_data(
        file_bytes,
        metadata={"source": file_path}
    )

    parser = PyMuPDFParser()
    docs = list(parser.lazy_parse(blob))

    file_name = os.path.basename(file_path)

    for doc in docs:
        doc.metadata["file_name"] = file_name

    return docs


def parse_multiple_pdfs(file_paths: List[str]) -> List[Document]:
    """
    Parse multiple PDF files and combine all documents into a single list.

    Args:
        file_paths (List[str]):
            List of PDF file paths.

    Returns:
        List[Document]:
            Combined list of LangChain Document objects from all PDFs.
    """
    all_docs = []

    for file_path in file_paths:
        docs = pdf_parser(file_path)
        all_docs.extend(docs)

    return all_docs