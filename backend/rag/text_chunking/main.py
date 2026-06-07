from langchain_text_splitters import MarkdownHeaderTextSplitter
# Char-level splits
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langsmith import traceable

# @traceable
def text_chunking(markdown_document: str):
    '''Markdown splitting followed by token-level splitting with chunk size of 512 tokens'''

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    # MD splits
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False
    )
    md_header_splits = markdown_splitter.split_text(markdown_document)

    chunk_size = 512
    chunk_overlap = 30
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Split
    splits = text_splitter.split_documents(md_header_splits)
    return splits
