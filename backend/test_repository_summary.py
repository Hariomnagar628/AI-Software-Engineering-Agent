
from app.services.repository_summary import get_repository_summary

result = get_repository_summary("/tmp/agent-test-repo")

assert result["repository"]["name"] == "agent-test-repo"
assert result["total_files"] == len(result["files"])
assert result["total_files"] == sum(result["statistics"].values())
assert "README.md" in result["files"]
assert ".md" in result["statistics"]

print("Repository summary test passed!")
print(result)
