
from app.services.repository_overview import get_repository_overview

result = get_repository_overview("/tmp/agent-test-repo")

print(result)

assert result["repository"]["name"] == "agent-test-repo"
assert isinstance(result["total_files"], int)
assert result["total_files"] == len(result["files"])
assert "README.md" in result["files"]
assert "main.py" in result["files"]

print("Repository overview service test passed!")
