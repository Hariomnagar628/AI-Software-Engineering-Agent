
from app.services.file_reader import read_repository_file
from app.services.code_parser import parse_python_source


def analyze_python_file(
    repository_path: str,
    relative_file_path: str,
) -> dict:
    """
    Read a Python file from a repository and extract its structure.
    """

    # Step 1: Read the file using the existing safety checks.
    file_data = read_repository_file(
        repository_path=repository_path,
        relative_file_path=relative_file_path,
    )

    # Step 2: Parse the file's source code.
    result = parse_python_source(
        source_code=file_data["content"],
        file_path=file_data["path"],
    )

    # Step 3: Add basic file metadata.
    result["size_bytes"] = file_data["size_bytes"]

    return result
