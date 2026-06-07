from pathlib import Path


def detect_file_type(file_path: str) -> str:
    """
    Detect file type from extension.
    """

    suffix = Path(file_path).suffix.lower()

    mapping = {
        ".pdf": "pdf",
        ".csv": "csv",
        ".xlsx": "xlsx",
        ".xls": "xlsx",
        ".docx": "docx",
    }

    if suffix not in mapping:
        raise ValueError(f"Unsupported file type: {suffix}")

    return mapping[suffix]