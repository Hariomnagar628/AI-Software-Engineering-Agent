from unittest.mock import MagicMock, patch

from app.services.repository_onboarding import onboard_repository


@patch("app.services.repository_onboarding.index_repository")
@patch("app.services.repository_onboarding.get_repository_overview")
@patch("app.services.repository_onboarding.inspect_repository")
@patch("app.services.repository_onboarding.clone_repository")
def test_onboard_repository(
    mock_clone,
    mock_inspect,
    mock_overview,
    mock_index,
):
    mock_clone.return_value = {
        "repository_name": "demo",
        "repository_url": "https://github.com/user/demo.git",
        "repository_path": "/workspace/demo",
        "status": "cloned",
    }

    mock_inspect.return_value = {
        "name": "demo",
        "root_path": "/workspace/demo",
        "branch": "main",
        "is_dirty": False,
    }

    mock_overview.return_value = {
        "total_files": 10,
        "files": ["main.py"],
    }

    mock_index.return_value = {
        "repository_path": "/workspace/demo",
        "total_files": 10,
        "total_chunks": 20,
        "inserted": 20,
        "skipped": 0,
        "errors": [],
    }

    db = MagicMock()

    result = onboard_repository(
        db=db,
        repository_url="https://github.com/user/demo.git",
    )

    assert result["repository_name"] == "demo"
    assert result["branch"] == "main"
    assert result["total_files"] == 10
    assert result["total_chunks"] == 20
    assert result["inserted_chunks"] == 20
    assert result["status"] == "indexed"

    mock_clone.assert_called_once()
    mock_inspect.assert_called_once_with("/workspace/demo")
    mock_overview.assert_called_once_with("/workspace/demo")
    mock_index.assert_called_once_with(
        db=db,
        repository_path="/workspace/demo",
    )


@patch("app.services.repository_onboarding.get_repository_overview")
@patch("app.services.repository_onboarding.inspect_repository")
@patch("app.services.repository_onboarding.clone_repository")
def test_onboard_empty_repository(
    mock_clone,
    mock_inspect,
    mock_overview,
):
    mock_clone.return_value = {
        "repository_name": "empty",
        "repository_url": "https://github.com/user/empty.git",
        "repository_path": "/workspace/empty",
        "status": "cloned",
    }

    mock_inspect.return_value = {
        "name": "empty",
        "root_path": "/workspace/empty",
        "branch": "main",
        "is_dirty": False,
    }

    mock_overview.return_value = {
        "total_files": 0,
        "files": [],
    }

    try:
        onboard_repository(
            db=MagicMock(),
            repository_url="https://github.com/user/empty.git",
        )
        assert False, "Expected ValueError for empty repository"

    except ValueError as exc:
        assert "supported source files" in str(exc)