from sqlalchemy.orm import Session

from app.services.repository_cloner import clone_repository
from app.services.repository_service import inspect_repository
from app.services.repository_overview import get_repository_overview
from app.services.repository_ingestion import index_repository


def onboard_repository(
    db: Session,
    repository_url: str,
) -> dict:
    """
    Clone, inspect, scan, and index a Git repository.
    """

    # Step 1: Clone the repository.
    clone_result = clone_repository(repository_url)

    repository_path = clone_result["repository_path"]

    # Step 2: Inspect the cloned repository.
    repository_info = inspect_repository(repository_path)

    # Step 3: Get repository overview.
    overview = get_repository_overview(repository_path)

    if overview["total_files"] == 0:
        raise ValueError(
            "Repository does not contain supported source files"
        )

    # Step 4: Generate embeddings and store code chunks.
    indexing_result = index_repository(
        db=db,
        repository_path=repository_path,
    )

    # Step 5: Return onboarding summary.
    return {
        "repository_name": clone_result["repository_name"],
        "repository_url": clone_result["repository_url"],
        "repository_path": repository_path,
        "clone_status": clone_result["status"],
        "branch": repository_info["branch"],
        "total_files": overview["total_files"],
        "total_chunks": indexing_result["total_chunks"],
        "inserted_chunks": indexing_result["inserted"],
        "skipped_chunks": indexing_result["skipped"],
        "indexing_errors": indexing_result["errors"],
        "status": "indexed",
    }