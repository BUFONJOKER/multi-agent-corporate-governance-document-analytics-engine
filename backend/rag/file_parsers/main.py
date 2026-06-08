from typing import List, Union

def parse_file(file_path: Union[str, List[str]], file_type: str):
    """
    Parses files dynamically based on file type.
    """
    if file_type == "pdf":
        # INLINE IMPORTS: Python only loads these if the file is a PDF!
        from rag.file_parsers.pdf.main import pdf_parser, parse_multiple_pdfs

        if isinstance(file_path, list):
            return parse_multiple_pdfs(file_path)
        return pdf_parser(file_path)

    elif file_type == "csv":
        # INLINE IMPORTS: Python only loads these if the file is a CSV!
        from rag.file_parsers.csv.main import csv_parser, parse_multiple_csvs

        if isinstance(file_path, list):
            return parse_multiple_csvs(file_path)
        return csv_parser(file_path)

    else:
        raise ValueError(f"Unsupported file type: {file_type}")