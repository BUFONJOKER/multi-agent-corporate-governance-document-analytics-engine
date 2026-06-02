from firecrawl import Firecrawl
from firecrawl.v2.types import ParseOptions
import streamlit as st
from config import FIRE_CRAWL_API

def parser(file_path: str, file_type: str):
    '''
    Parses a File using Firecrawl's API and returns the content in Markdown format.
    '''

    app = Firecrawl(api_key=FIRE_CRAWL_API)

    # 1. Open the file in Binary Read mode ('rb')
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # 2. Use app.parse and provide the bytes alongside metadata
    doc = app.parse(
        file_bytes,
        filename=file_path,
        content_type=f"text/{file_type}",
        options=ParseOptions(formats=["markdown"])
    )

    return doc.markdown