
import hashlib
from pathlib import PurePosixPath
from app.services.file_reader import read_repository_file
from app.services.file_scanner import scan_repository


def detect_language(file_path: str) -> str:
    """Identify a programming language from the file extension."""
    extension = PurePosixPath(file_path).suffix.lower()

    languages = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "c",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".yaml": "yaml",
        ".yml": "yaml",
    }

    if PurePosixPath(file_path).name == "Dockerfile":
        return "dockerfile"

    return languages.get(extension, "text")


def generate_chunk_id(
    file_path: str,
    start_line: int,
    end_line: int,
    content: str,
) -> str:
    """Generate a deterministic ID for a source-code chunk."""
    raw_value = (
        f"{file_path}:{start_line}:{end_line}:{content}"
    )

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def chunk_source_code(
    content: str,
    file_path: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[dict]:
    """
    Split source code into overlapping character-based chunks.

    Line numbers are preserved so retrieved chunks can be
    traced back to their original source file.
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    if not content:
        return []

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(content):
        end = min(start + chunk_size, len(content))

        chunk_content = content[start:end]

        start_line = content.count("\n", 0, start) + 1
        end_line = content.count("\n", 0, end)

        if end == len(content) and content.endswith("\n"):
            end_line += 1

        # Avoid counting an empty trailing line as source content.
        end_line = max(start_line, end_line)

        chunk_id = generate_chunk_id(
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            content=chunk_content,
        )

        chunks.append({
            "id": chunk_id,
            "content": chunk_content,
            "metadata": {
                "file_path": file_path,
                "language": detect_language(file_path),
                "chunk_index": chunk_index,
                "start_line": start_line,
                "end_line": end_line,
            },
        })

        chunk_index += 1

        if end == len(content):
            break

        start = end - overlap

    return chunks



def chunk_repository(
    repository_path: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> dict:
    """Read repository files and generate code chunks."""
    files = scan_repository(repository_path)

    all_chunks = []
    errors = []

    for file_path in files:
        try:
            file_data = read_repository_file(
                repository_path=repository_path,
                relative_file_path=file_path,
            )

            chunks = chunk_source_code(
                content=file_data["content"],
                file_path=file_path,
                chunk_size=chunk_size,
                overlap=overlap,
            )

            all_chunks.extend(chunks)

        except ValueError as exc:
            errors.append({
                "file_path": file_path,
                "error": str(exc),
            })

    return {
        "repository_path": repository_path,
        "total_files": len(files),
        "total_chunks": len(all_chunks),
        "chunks": all_chunks,
        "errors": errors,
    }

