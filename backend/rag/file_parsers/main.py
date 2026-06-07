from rag.file_parsers.pdf.main import pdf_parser
from rag.file_parsers.csv.csv_parser import csv_parser


def parse_file(file_path: str, file_type: str):
    '''Parses a file based on its type.'''

    if file_type in 'pdf':
        return pdf_parser(file_path)
    elif file_type == "csv":
        return csv_parser(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


if __name__ == "__main__":
    # Example usage
    file_type = input("Enter the file type (pdf, docx, xlsx, csv):")
    file_path = input("Enter the file path:")

    try:
        result = parse_file(file_path, file_type)
        print("Parsed Data:", result)

    except ValueError as e:
        print("Error:", str(e))
