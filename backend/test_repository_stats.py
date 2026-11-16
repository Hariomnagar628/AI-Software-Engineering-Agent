
from app.services.repository_stats import get_repository_stats

result = get_repository_stats("/tmp/agent-test-repo")

print(result)

assert result["total_files"] > 0
assert result["total_files"] == sum(
    result["extension_counts"].values()
)

assert ".py" in result["extension_counts"]
assert ".md" in result["extension_counts"]

print("Repository statistics service test passed!")
