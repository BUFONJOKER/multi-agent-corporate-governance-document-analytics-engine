from langchain_community.document_loaders import CSVLoader

def compile_docs_to_markdown(documents):
    markdown_lines = []

    # 1. Add a primary document title
    markdown_lines.append("# Corporate Governance Analytics Engine - Task List\n")
    markdown_lines.append("This file aggregates all parsed task records into a single markdown index.\n")
    markdown_lines.append("--- \n")

    # 2. Iterate through each document item
    for doc in documents:
        # Extract metadata for tracking
        row_num = doc.metadata.get('row', 'Unknown')

        # Format the page_content slightly to separate elements cleanly
        # Replacing original newlines with Markdown list bullet structures
        formatted_content = doc.page_content.replace("\n", "\n* ")

        # 3. Append as a distinct Markdown Section
        markdown_lines.append(f"## Document Row #{row_num}")
        markdown_lines.append(f"* {formatted_content}")
        markdown_lines.append("\n---") # Separator between records

    # 4. Join everything with newlines
    final_markdown = "\n".join(markdown_lines)

    return final_markdown

def csv_parser(file_path: str):
    '''
    Parse a CSV file and return a list of documents, where each document represents a single row transformed into key-value text strings.
    '''

    loader = CSVLoader(
        file_path=file_path,
        csv_args={
            "delimiter": ",",
            "quotechar": '"',
        }
    )
    docs = loader.load()

    docs = compile_docs_to_markdown(docs)
    # Each doc represents a single row transformed into key-value text strings
    return docs
