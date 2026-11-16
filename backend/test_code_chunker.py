
from app.services.code_chunker import (
    chunk_source_code,
    chunk_repository,
    detect_language,
)


# Test language detection.
assert detect_language("payment_service.py") == "python"
assert detect_language("app.ts") == "typescript"
assert detect_language("Dockerfile") == "dockerfile"


# Test chunking.
source = "\n".join(
    f"def function_{i}(): return {i}"
    for i in range(20)
)

chunks = chunk_source_code(
    content=source,
    file_path="payment_service.py",
    chunk_size=100,
    overlap=20,
)

assert len(chunks) > 1

# Check metadata.
first_chunk = chunks[0]

assert first_chunk["metadata"]["file_path"] == "payment_service.py"
assert first_chunk["metadata"]["language"] == "python"
assert first_chunk["metadata"]["chunk_index"] == 0
assert first_chunk["metadata"]["start_line"] == 1

# Check stable IDs.
same_chunks = chunk_source_code(
    content=source,
    file_path="payment_service.py",
    chunk_size=100,
    overlap=20,
)

assert chunks[0]["id"] == same_chunks[0]["id"]

# Check IDs change when source changes.
different_chunks = chunk_source_code(
    content="# updated\n" + source,
    file_path="payment_service.py",
    chunk_size=100,
    overlap=20,
)

assert chunks[0]["id"] != different_chunks[0]["id"]

# Check invalid configuration.
try:
    chunk_source_code(
        content=source,
        file_path="payment_service.py",
        chunk_size=100,
        overlap=100,
    )
except ValueError:
    pass
else:
    raise AssertionError("Invalid overlap should fail.")

# Test actual repository chunking.
repository_result = chunk_repository(
    repository_path="/tmp/agent-test-repo",
    chunk_size=1200,
    overlap=200,
)

assert repository_result["total_files"] > 0
assert repository_result["total_chunks"] > 0

print("Code chunker tests passed!")
print("Files scanned:", repository_result["total_files"])
print("Chunks generated:", repository_result["total_chunks"])
