
from pathlib import Path

import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError


def inspect_repository(repository_path: str) -> dict:
    """
    Validate a local Git repository and return basic metadata.
    """

    path = Path(repository_path).expanduser().resolve()

    if not path.exists():
        raise ValueError("Repository path does not exist.")

    if not path.is_dir():
        raise ValueError("Repository path must be a directory.")

    try:
        repo = git.Repo(path, search_parent_directories=False)
    except (InvalidGitRepositoryError, NoSuchPathError):
        raise ValueError("The provided directory is not a valid Git repository.")

    if repo.bare:
        raise ValueError("Bare Git repositories are not supported.")

    try:
        branch = repo.active_branch.name
    except TypeError:
        branch = None

    return {
        "name": path.name,
        "root_path": str(path),
        "branch": branch,
        "is_dirty": repo.is_dirty(untracked_files=True),
    }
