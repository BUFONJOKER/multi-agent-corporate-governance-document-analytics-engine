from rag.file_parsers.pdf.main import pdf_parser
from rag.file_parsers.csv.main import csv_parser


def parse_file(file_path: str, file_type: str):
    '''Parses a file based on its type.'''

    if file_type in 'pdf':
        return pdf_parser(file_path)
    elif file_type == "csv":
        return csv_parser(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
