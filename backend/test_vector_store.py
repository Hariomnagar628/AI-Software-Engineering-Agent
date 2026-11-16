
from app.core.database import SessionLocal, Base, engine
from app.models.code_chunk import CodeChunk
from app.services.vector_store import store_code_chunks
from app.services.embedding_service import (
    EMBEDDING_DIMENSION,
)


Base.metadata.create_all(bind=engine)

repository_path = "/tmp/vector-store-test"

test_chunk = {
    "id": "a" * 64,
    "content": "def validate_user(user_id): return bool(user_id)",
    "metadata": {
        "file_path": "user_service.py",
        "language": "python",
        "chunk_index": 0,
        "start_line": 1,
        "end_line": 1,
    },
    "embedding": [0.1] * EMBEDDING_DIMENSION,
    "embedding_model": "gemini-embedding-2",
}

db = SessionLocal()

try:
    # Clean up any previous test record.
    db.query(CodeChunk).filter(
        CodeChunk.repository_path == repository_path
    ).delete()
    db.commit()

    # First insertion.
    result = store_code_chunks(
        db=db,
        repository_path=repository_path,
        embedded_chunks=[test_chunk],
    )

    assert result["inserted"] == 1
    assert result["skipped"] == 0

    # Verify the record exists.
    saved = db.query(CodeChunk).filter(
        CodeChunk.repository_path == repository_path,
        CodeChunk.chunk_id == test_chunk["id"],
    ).first()

    assert saved is not None
    assert saved.file_path == "user_service.py"
    assert saved.content == test_chunk["content"]
    assert len(saved.embedding) == EMBEDDING_DIMENSION

    # Test duplicate prevention.
    duplicate_result = store_code_chunks(
        db=db,
        repository_path=repository_path,
        embedded_chunks=[test_chunk],
    )

    assert duplicate_result["inserted"] == 0
    assert duplicate_result["skipped"] == 1

    print("Vector store tests passed!")

finally:
    # Remove test records.
    db.query(CodeChunk).filter(
        CodeChunk.repository_path == repository_path
    ).delete()
    db.commit()
    db.close()
