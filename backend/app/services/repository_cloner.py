import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError


# Store cloned repositories outside the backend source directory.
WORKSPACE_DIR = Path(__file__).resolve().parents[3] / "workspace"

ALLOWED_GIT_HOSTS = {
    "github.com",
    "gitlab.com",
    "bitbucket.org",
}


def validate_repository_url(repository_url: str) -> str:
    """
    Validate a public HTTPS Git repository URL.
    """

    if not repository_url or not repository_url.strip():
        raise ValueError("Repository URL cannot be empty")

    repository_url = repository_url.strip()
    parsed_url = urlparse(repository_url)

    if parsed_url.scheme != "https":
        raise ValueError("Only HTTPS repository URLs are supported")

    if not parsed_url.hostname:
        raise ValueError("Invalid repository URL")

    if parsed_url.username or parsed_url.password:
        raise ValueError(
            "Do not include credentials in the repository URL"
        )

    hostname = parsed_url.hostname.lower()

    if hostname not in ALLOWED_GIT_HOSTS:
        raise ValueError(
            "Supported hosts are GitHub, GitLab, and Bitbucket"
        )

    if not parsed_url.path or parsed_url.path == "/":
        raise ValueError("Repository path is missing from the URL")

    # Prevent malformed paths and unexpected URL components.
    path_parts = [
        part for part in parsed_url.path.strip("/").split("/")
        if part
    ]

    if len(path_parts) < 2:
        raise ValueError("URL must contain an owner and repository name")

    if any(part in {".", ".."} for part in path_parts):
        raise ValueError("Invalid repository path")

    if parsed_url.query or parsed_url.fragment:
        raise ValueError("Repository URL cannot contain query or fragment")

    return repository_url.rstrip("/")


def get_repository_name(repository_url: str) -> str:
    """
    Extract a safe repository name from the URL.
    """

    parsed_url = urlparse(repository_url)
    repository_name = parsed_url.path.rstrip("/").split("/")[-1]

    if repository_name.lower().endswith(".git"):
        repository_name = repository_name[:-4]

    repository_name = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        repository_name,
    )

    if not repository_name:
        raise ValueError("Could not determine repository name")

    return repository_name


def clone_repository(repository_url: str) -> dict:
    """
    Clone a Git repository into the agent workspace.
    """

    repository_url = validate_repository_url(repository_url)

    repository_name = get_repository_name(repository_url)

    # Hash the URL to avoid collisions between repositories
    # that have the same name but different owners or hosts.
    repository_hash = hashlib.sha256(
        repository_url.encode("utf-8")
    ).hexdigest()[:12]

    destination = WORKSPACE_DIR / f"{repository_name}-{repository_hash}"

    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        try:
            existing_repo = Repo(
                destination,
                search_parent_directories=False,
            )

            existing_url = existing_repo.remotes.origin.url

            if existing_url.rstrip("/") != repository_url:
                raise ValueError(
                    "Workspace directory contains a different repository"
                )

            return {
                "repository_name": repository_name,
                "repository_url": repository_url,
                "repository_path": str(destination.resolve()),
                "status": "already_cloned",
            }

        except InvalidGitRepositoryError as exc:
            raise ValueError(
                "Destination exists but is not a valid Git repository"
            ) from exc

    try:
        Repo.clone_from(
            repository_url,
            destination,
        )

    except GitCommandError as exc:
        raise ValueError(
            "Unable to clone repository. Check the URL, "
            "repository access, and network connection."
        ) from exc

    return {
        "repository_name": repository_name,
        "repository_url": repository_url,
        "repository_path": str(destination.resolve()),
        "status": "cloned",
    }