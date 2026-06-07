import os
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import CSVLoader



def csv_parser(file_path: str) -> List[Document]:
    """
    Parse a CSV file into LangChain Document objects.

    Each row in the CSV becomes a separate Document. Additional metadata
    is added to support source attribution during retrieval.

    Args:
        file_path (str):
            Path to the CSV file.

    Returns:
        List[Document]:
            List of Document objects representing CSV rows.
    """

    loader = CSVLoader(
        file_path=file_path,
        csv_args={
            "delimiter": ",",
            "quotechar": '"',
        }
    )

    docs = loader.load()

    file_name = os.path.basename(file_path)

    for doc in docs:
        doc.metadata["file_name"] = file_name
        doc.metadata["file_type"] = "csv"

    return docs





def parse_multiple_csvs(file_paths: List[str]) -> List[Document]:
    """
    Parse multiple CSV files into a single document collection.

    Args:
        file_paths (List[str]):
            List of CSV file paths.

    Returns:
        List[Document]:
            Combined documents from all CSV files.
    """

    all_docs = []

    for file_path in file_paths:
        docs = csv_parser(file_path)
        all_docs.extend(docs)

    return all_docs