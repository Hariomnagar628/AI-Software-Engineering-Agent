from sqlalchemy.orm import Session

from app.services.semantic_search import search_similar_code


MAX_CONTEXT_CHARS = 12000


def build_retrieval_context(
    chunks: list[dict],
    max_context_chars: int = MAX_CONTEXT_CHARS,
) -> dict:
    """
    Build an LLM-ready context from retrieved code chunks.

    Each source includes its file path and line numbers.
    """

    if max_context_chars < 1:
        raise ValueError("max_context_chars must be greater than 0")

    context_parts = []
    sources = []
    used_chunk_ids = set()
    current_length = 0

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]

        # Avoid including the same chunk more than once.
        if chunk_id in used_chunk_ids:
            continue

        source_id = f"S{len(sources) + 1}"

        file_path = chunk["file_path"]
        start_line = chunk["start_line"]
        end_line = chunk["end_line"]
        content = chunk["content"]

        header = (
            f"[{source_id}] {file_path}:"
            f"{start_line}-{end_line}\n"
        )

        remaining = max_context_chars - current_length

        if remaining <= len(header):
            break

        available_content = remaining - len(header) - 2

        if available_content <= 0:
            break

        # Keep the context within the configured character limit.
        included_content = content[:available_content]

        context_part = (
            f"{header}"
            f"{included_content}\n"
        )

        context_parts.append(context_part)
        current_length += len(context_part)

        used_chunk_ids.add(chunk_id)

        sources.append({
            "source_id": source_id,
            "chunk_id": chunk_id,
            "file_path": file_path,
            "start_line": start_line,
            "end_line": end_line,
            "similarity_score": chunk["similarity_score"],
        })

        # Stop if the current chunk had to be truncated.
        if len(included_content) < len(content):
            break

    return {
        "context": "\n".join(context_parts),
        "sources": sources,
    }


def retrieve_code_context(
    db: Session,
    repository_path: str,
    query: str,
    limit: int = 5,
    max_context_chars: int = MAX_CONTEXT_CHARS,
) -> dict:
    """
    Retrieve relevant code and prepare context for an LLM.
    """

    if not repository_path.strip():
        raise ValueError("Repository path cannot be empty")

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if limit < 1 or limit > 50:
        raise ValueError("Limit must be between 1 and 50")

    # Step 1: Find semantically similar code chunks.
    retrieval_result = search_similar_code(
        db=db,
        repository_path=repository_path,
        query=query,
        limit=limit,
    )

    retrieved_chunks = retrieval_result["results"]

    # Step 2: Build context and source references.
    context_result = build_retrieval_context(
        chunks=retrieved_chunks,
        max_context_chars=max_context_chars,
    )

    # Step 3: Return everything in one structured response.
    return {
        "repository_path": repository_path,
        "query": query,
        "total_retrieved": len(retrieved_chunks),
        "total_sources": len(context_result["sources"]),
        "retrieved_chunks": retrieved_chunks,
        "context": context_result["context"],
        "sources": context_result["sources"],
    }