
from app.core.database import SessionLocal
from app.services.semantic_search import search_similar_code


REPOSITORY_PATH = "/tmp/agent-test-repo"

db = SessionLocal()

try:
    # Check that the repository has indexed chunks.
    from app.models.code_chunk import CodeChunk

    count = (
        db.query(CodeChunk)
        .filter(
            CodeChunk.repository_path == REPOSITORY_PATH
        )
        .count()
    )

    assert count > 0, (
        "No indexed chunks found. Run repository indexing first."
    )

    # Perform semantic search.
    result = search_similar_code(
        db=db,
        repository_path=REPOSITORY_PATH,
        query="Where is payment processing implemented?",
        limit=5,
    )

    assert result["total_results"] > 0
    assert len(result["results"]) <= 5

    for item in result["results"]:
        assert item["chunk_id"]
        assert item["file_path"]
        assert item["content"]
        assert item["similarity_score"] is not None

    print("Semantic search integration test passed!")
    print("Results:", result["total_results"])

    for item in result["results"]:
        print(
            item["file_path"],
            item["start_line"],
            item["similarity_score"],
        )

finally:
    db.close()
