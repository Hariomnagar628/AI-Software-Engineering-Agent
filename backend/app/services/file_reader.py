
from pathlib import Path

from app.services.file_scanner import (
    ALLOWED_EXTENSIONS,
    IGNORED_EXTENSIONS,
    IGNORED_FILENAMES,
    IGNORED_DIRECTORIES,
)

MAX_FILE_SIZE = 1_000_000  # 1 MB


def read_repository_file(
    repository_path: str,
    relative_file_path: str,
) -> dict:
    """
    Read a supported text file inside a Git repository.
    The requested file path must be relative to the repository root.
    """

    root = Path(repository_path).expanduser().resolve()

    if not root.is_dir() or not (root / ".git").exists():
        raise ValueError("A valid Git repository root is required.")

    requested = Path(relative_file_path)

    if requested.is_absolute() or not relative_file_path:
        raise ValueError("Provide a non-empty relative file path.")

    if ".." in requested.parts:
        raise ValueError("Parent-directory traversal is not allowed.")

    # Reject symlinks in every component of the requested path.
    current = root
    for part in requested.parts:
        current = current / part

        if current.is_symlink():
            raise ValueError("Symbolic links are not allowed.")

    file_path = current

    # Resolve and confirm the final path remains within the repository.
    try:
        file_path.resolve().relative_to(root)
    except ValueError as exc:
        raise ValueError("File must be inside the repository.") from exc

    if not file_path.is_file():
        raise ValueError("The requested file does not exist.")

    if any(part in IGNORED_DIRECTORIES for part in requested.parts):
        raise ValueError("Files inside ignored directories cannot be read.")

    filename = file_path.name
    suffix = file_path.suffix.lower()

    if filename in IGNORED_FILENAMES:
        raise ValueError("Sensitive files cannot be read.")

    if filename.endswith(".env") or filename.startswith(".env."):
        raise ValueError("Environment files cannot be read.")

    if suffix in IGNORED_EXTENSIONS:
        raise ValueError("Private key and certificate files cannot be read.")

    if (
        suffix not in ALLOWED_EXTENSIONS
        and filename.lower() not in {"dockerfile", "makefile"}
    ):
        raise ValueError("Unsupported file type.")

    if file_path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File exceeds the 1 MB size limit.")

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("File is not valid UTF-8 text.") from exc

    return {
        "path": requested.as_posix(),
        "content": content,
        "size_bytes": file_path.stat().st_size,
    }
