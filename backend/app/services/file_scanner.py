
from pathlib import Path

# Directories that should not be scanned.
IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".pytest_cache",
    ".mypy_cache",
    "site-packages",
}

# File types useful for understanding a codebase.
ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".php",
    ".rb",
    ".sql",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".md",
    ".txt",
    ".sh",
    ".dockerfile",
}

# Sensitive filenames that should never be indexed.
IGNORED_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
}

# File extensions that may contain private keys or certificates.
IGNORED_EXTENSIONS = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}


def scan_repository(repository_path: str) -> list[str]:
    """
    Return eligible repository files as paths relative to the repository root.
    """

    root = Path(repository_path).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise ValueError("Repository path must be an existing directory.")

    # Require a Git repository root.
    if not (root / ".git").exists():
        raise ValueError("The directory must be a Git repository root.")

    files: list[str] = []

    for current_dir, directories, filenames in __import__("os").walk(
        root,
        followlinks=False,
    ):
        current_path = Path(current_dir)

        # Skip ignored directories and symlinked directories.
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
            and not (current_path / directory).is_symlink()
        ]

        for filename in filenames:
            file_path = current_path / filename

            if file_path.is_symlink() or not file_path.is_file():
                continue

            if filename in IGNORED_FILENAMES:
                continue

            if filename.endswith(".env") or filename.startswith(".env."):
                continue

            if file_path.suffix.lower() in IGNORED_EXTENSIONS:
                continue

            if (
                file_path.suffix.lower() not in ALLOWED_EXTENSIONS
                and filename.lower() != "dockerfile"
                and filename.lower() != "makefile"
            ):
                continue

            relative_path = file_path.relative_to(root)
            files.append(relative_path.as_posix())

    return sorted(files)
