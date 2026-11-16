
from app.services.file_reader import read_repository_file

ROOT = "/tmp/agent-test-repo"

# Test 1: Read a valid source file.
result = read_repository_file(ROOT, "main.py")

assert result["path"] == "main.py"
assert "hello" in result["content"]
assert result["size_bytes"] > 0

print("Valid file test passed!")

# Test 2: Read repository documentation.
result = read_repository_file(ROOT, "README.md")

assert "# Test repository" in result["content"]

print("README test passed!")

# Test 3: Reject a secret file.
try:
    read_repository_file(ROOT, ".env")
except ValueError:
    print("Secret file rejection test passed!")
else:
    raise AssertionError("The reader accepted a secret file.")

# Test 4: Reject parent-directory traversal.
try:
    read_repository_file(ROOT, "../outside.py")
except ValueError:
    print("Path traversal test passed!")
else:
    raise AssertionError("The reader accepted a traversal path.")

print("All file reader tests passed!")
