import pytest

from app.services.repository_cloner import (
    validate_repository_url,
    get_repository_name,
)


def test_valid_github_url():
    url = "https://github.com/owner/project.git"

    result = validate_repository_url(url)

    assert result == url


def test_valid_gitlab_url():
    url = "https://gitlab.com/owner/project"

    result = validate_repository_url(url)

    assert result == url


def test_get_repository_name():
    url = "https://github.com/owner/my-project.git"

    result = get_repository_name(url)

    assert result == "my-project"


def test_reject_http_url():
    with pytest.raises(ValueError):
        validate_repository_url(
            "http://github.com/owner/project.git"
        )


def test_reject_unsupported_host():
    with pytest.raises(ValueError):
        validate_repository_url(
            "https://example.com/owner/project.git"
        )


def test_reject_empty_url():
    with pytest.raises(ValueError):
        validate_repository_url("")


def test_reject_missing_repository_path():
    with pytest.raises(ValueError):
        validate_repository_url("https://github.com/")