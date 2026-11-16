
from app.services.repository_service import inspect_repository

repository = inspect_repository("/tmp/agent-test-repo")

print(repository)
