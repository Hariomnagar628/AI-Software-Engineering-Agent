
from app.services.repository_service import inspect_repository
from app.services.file_scanner import scan_repository


def get_repository_overview(repository_path: str) -> dict:
    """
    Return repository metadata and a list of eligible files.
    """

    # 1. Validate the repository and get its Git metadata.
    repository = inspect_repository(repository_path)

    # 2. Discover eligible source and documentation files.
    files = scan_repository(repository_path)

    # 3. Combine both results into one overview.
    return {
        "repository": repository,
        "total_files": len(files),
        "files": files,
    }
