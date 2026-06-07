from typing import List, Union

from rag.file_parsers.pdf.main import (
    pdf_parser,
    parse_multiple_pdfs,
)

from rag.file_parsers.csv.main import (
    csv_parser,
    parse_multiple_csvs,
)


def parse_file(file_path: str | List[str], file_type: str):
    """
    Parse files based on type.
    """

    if file_type == "pdf":
        if isinstance(file_path, list):
            return parse_multiple_pdfs(file_path)
        return pdf_parser(file_path)

    elif file_type == "csv":
        if isinstance(file_path, list):
            return parse_multiple_csvs(file_path)
        return csv_parser(file_path)

    else:
        raise ValueError(f"Unsupported file type: {file_type}")