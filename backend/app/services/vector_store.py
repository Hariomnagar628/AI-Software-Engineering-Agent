
from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk
from app.services.embedding_service import EMBEDDING_DIMENSION


def store_code_chunks(
    db: Session,
    repository_path: str,
    embedded_chunks: list[dict],
) -> dict:
    """
    Store embedded code chunks in PostgreSQL.

    Existing chunks with the same repository path and chunk ID
    are skipped, making repeated indexing idempotent.
    """
    if not repository_path.strip():
        raise ValueError("Repository path cannot be empty.")

    if not embedded_chunks:
        return {
            "total_received": 0,
            "inserted": 0,
            "skipped": 0,
        }

    chunk_ids = [
        chunk["id"] for chunk in embedded_chunks
    ]

    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Duplicate chunk IDs found in input.")

    existing_ids = set(
        db.query(CodeChunk.chunk_id)
        .filter(
            CodeChunk.repository_path == repository_path,
            CodeChunk.chunk_id.in_(chunk_ids),
        )
        .all()
    )

    # SQLAlchemy returns one-element tuples from this query.
    existing_ids = {
        item[0] for item in existing_ids
    }

    records = []

    for chunk in embedded_chunks:
        metadata = chunk["metadata"]
        embedding = chunk["embedding"]

        if len(embedding) != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Invalid embedding dimension for {chunk['id']}. "
                f"Expected {EMBEDDING_DIMENSION}, "
                f"received {len(embedding)}."
            )

        if not chunk["content"].strip():
            raise ValueError("Chunk content cannot be empty.")

        if chunk["id"] in existing_ids:
            continue

        records.append(
            CodeChunk(
                chunk_id=chunk["id"],
                repository_path=repository_path,
                file_path=metadata["file_path"],
                language=metadata["language"],
                chunk_index=metadata["chunk_index"],
                start_line=metadata["start_line"],
                end_line=metadata["end_line"],
                content=chunk["content"],
                embedding=embedding,
                embedding_model=chunk["embedding_model"],
                chunk_metadata=metadata,
            )
        )

    try:
        db.add_all(records)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "total_received": len(embedded_chunks),
        "inserted": len(records),
        "skipped": len(embedded_chunks) - len(records),
    }
