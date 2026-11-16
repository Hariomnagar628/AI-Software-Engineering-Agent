
from collections import Counter
from pathlib import PurePosixPath

from app.services.file_scanner import scan_repository


def get_repository_stats(repository_path: str) -> dict:
    """
    Calculate file counts by extension for a Git repository.
    """

    files = scan_repository(repository_path)

    extension_counts = Counter()

    for file_path in files:
        filename = PurePosixPath(file_path).name

        if filename.lower() == "dockerfile":
            extension = "Dockerfile"
        elif filename.lower() == "makefile":
            extension = "Makefile"
        else:
            extension = PurePosixPath(file_path).suffix.lower()

            if not extension:
                extension = "[no extension]"

        extension_counts[extension] += 1

    return {
        "total_files": len(files),
        "extension_counts": dict(sorted(extension_counts.items())),
    }
