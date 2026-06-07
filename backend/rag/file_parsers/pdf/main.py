import os
from langchain_core.document_loaders import Blob
from langchain_community.document_loaders.parsers.pdf import PyMuPDFParser

from langchain_core.documents import Document

def convert_docs_to_single_markdown(docs: list[Document]) -> str:
    """
    Compiles a list of LangChain Document objects into a single Markdown string
    """
    markdown_segments = []

    # Optional: Add a master title block if you have document source metadata
    if docs and "source" in docs[0].metadata:
        source_name = os.path.basename(docs[0].metadata["source"])
        markdown_segments.append(f"# Document: {source_name}\n\n---\n")

    for i, doc in enumerate(docs):
        # Extract page number from metadata if available (defaults to list index + 1)
        page_num = doc.metadata.get("page", i + 1)

        # 1. Add a structural Markdown header for each page/chunk boundary
        markdown_segments.append(f"## Page {page_num}\n")

        # 2. Append the actual text content of the document chunk
        markdown_segments.append(doc.page_content)

        # 3. Add a spacing trailing line break or horizontal rule between pages
        markdown_segments.append("\n\n---\n")

    # Join everything into a single master string
    final_markdown = "\n".join(markdown_segments)

    return final_markdown

def pdf_parser(file_path: str) -> str:
    '''
    Parses a File using PyMuPDFParser and returns the content in Markdown format.
    '''

    # 1. Parse the PDF to LangChain Docs
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    blob = Blob.from_data(file_bytes, metadata={"source": file_path})
    parser = PyMuPDFParser()
    docs = list(parser.lazy_parse(blob))


    markdown = convert_docs_to_single_markdown(docs)


    return markdown
