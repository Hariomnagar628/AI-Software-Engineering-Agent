
from app.services.file_scanner import scan_repository

files = scan_repository("/tmp/agent-test-repo")

print("Files discovered:")
for file_path in files:
    print(file_path)

assert "README.md" in files
assert not any(path.startswith(".git/") for path in files)
assert "main.py" in files
assert ".env" not in files
assert "venv/ignored.py" not in files
assert "node_modules/ignored.js" not in files

print("Scanner test passed!")
