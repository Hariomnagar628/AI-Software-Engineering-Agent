
from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk
from app.services.embedding_service import (
    generate_query_embedding,
    EMBEDDING_DIMENSION,
)


def search_similar_code(
    db: Session,
    repository_path: str,
    query: str,
    limit: int = 5,
) -> dict:
    """
    Search code chunks using Gemini embeddings and pgvector.
    """

    if not repository_path.strip():
        raise ValueError("Repository path cannot be empty.")

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if limit < 1 or limit > 50:
        raise ValueError("Limit must be between 1 and 50.")

    # Step 1: Convert the developer question into an embedding.
    query_embedding = generate_query_embedding(query)

    if len(query_embedding) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION} embedding dimensions, "
            f"received {len(query_embedding)}."
        )

    # Step 2: Calculate cosine distance in PostgreSQL.
    distance_expression = (
        CodeChunk.embedding.cosine_distance(query_embedding)
    )

    # Step 3: Retrieve the most similar code chunks.
    results = (
        db.query(
            CodeChunk,
            distance_expression.label("distance"),
        )
        .filter(
            CodeChunk.repository_path == repository_path
        )
        .order_by(distance_expression)
        .limit(limit)
        .all()
    )

    # Step 4: Format the retrieved results.
    matches = []

    for chunk, distance in results:
        matches.append({
            "chunk_id": chunk.chunk_id,
            "file_path": chunk.file_path,
            "language": chunk.language,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "content": chunk.content,
            "similarity_score": round(1 - float(distance), 4),
            "metadata": chunk.chunk_metadata,
        })

    return {
        "repository_path": repository_path,
        "query": query,
        "total_results": len(matches),
        "results": matches,
    }
