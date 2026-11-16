
from app.services.code_chunker import chunk_repository
from app.services.embedding_service import (
    generate_document_embeddings_batch,
)
from app.services.vector_store import store_code_chunks


def index_repository(
    db,
    repository_path: str,
) -> dict:
    """
    Complete repository ingestion:
    scan -> chunk -> embed -> store.
    """

    # Step 1: Generate source-code chunks.
    chunk_result = chunk_repository(
        repository_path=repository_path,
        chunk_size=1200,
        overlap=200,
    )

    chunks = chunk_result["chunks"]

    if not chunks:
        return {
            "repository_path": repository_path,
            "total_files": chunk_result["total_files"],
            "total_chunks": 0,
            "inserted": 0,
            "skipped": 0,
            "errors": chunk_result["errors"],
        }

    # Step 2: Generate Gemini embeddings in batches.
    embedded_chunks = generate_document_embeddings_batch(
        chunks=chunks,
        batch_size=16,
    )

    # Step 3: Store chunks and embeddings in PostgreSQL.
    storage_result = store_code_chunks(
        db=db,
        repository_path=repository_path,
        embedded_chunks=embedded_chunks,
    )

    return {
        "repository_path": repository_path,
        "total_files": chunk_result["total_files"],
        "total_chunks": len(chunks),
        "inserted": storage_result["inserted"],
        "skipped": storage_result["skipped"],
        "errors": chunk_result["errors"],
    }
