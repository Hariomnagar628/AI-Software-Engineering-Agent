
import math
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.core.config import settings


from google.genai import errors


# Load backend/.env
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)

# Gemini configuration
MODEL_NAME = "gemini-embedding-2"
EMBEDDING_DIMENSION = 768


def create_gemini_client(api_key: str | None = None):
    """Create a Gemini client using the configured API key."""
    key = (
        api_key
        or settings.gemini_api_key
        or os.getenv("GEMINI_API_KEY")
    )

    if not key:
        raise ValueError(
            "GEMINI_API_KEY not found. "
            "Check your backend/.env file."
        )

    return genai.Client(api_key=key)


def prepare_code_document(
    content: str,
    title: str | None = None,
) -> str:
    """Prepare source code for code-retrieval embedding."""
    return f"title: {title or 'none'} | text: {content}"


def prepare_code_query(query: str) -> str:
    """Prepare a natural-language query for code retrieval."""
    return f"task: code retrieval | query: {query}"


def generate_embedding(
    text: str,
    api_key: str | None = None,
) -> list[float]:
    """Generate an embedding using Gemini."""

    if not text.strip():
        raise ValueError("Text cannot be empty.")

    client = create_gemini_client(api_key)

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )

    if not response.embeddings:
        raise ValueError("Gemini returned no embeddings.")

    values = response.embeddings[0].values

    if not values:
        raise ValueError("Gemini returned an empty embedding.")

    if len(values) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION} dimensions, "
            f"received {len(values)}."
        )

    return [float(value) for value in values]


def generate_document_embedding(
    content: str,
    title: str | None = None,
) -> list[float]:
    """Generate an embedding for a code chunk."""
    prepared_text = prepare_code_document(content, title)
    return generate_embedding(prepared_text)


def generate_query_embedding(query: str) -> list[float]:
    """Generate an embedding for a developer's search query."""
    prepared_query = prepare_code_query(query)
    return generate_embedding(prepared_query)


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if not vector_a or not vector_b:
        raise ValueError("Vectors cannot be empty.")

    if len(vector_a) != len(vector_b):
        raise ValueError("Vector dimensions must match.")

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        raise ValueError("Zero vectors cannot be compared.")

    return dot_product / (norm_a * norm_b)


def split_into_batches(
    items: list,
    batch_size: int,
) -> list[list]:
    """Split a list into smaller batches."""

    if batch_size <= 0:
        raise ValueError("Batch size must be greater than zero.")

    return [
        items[index:index + batch_size]
        for index in range(0, len(items), batch_size)
    ]


def embed_content_with_retry(
    client,
    contents,
    max_retries: int = 3,
):
    """
    Call Gemini with retry handling for rate limits
    and temporary server errors.
    """

    for attempt in range(max_retries):
        try:
            response = client.models.embed_content(
                model=MODEL_NAME,
                contents=contents,
                config=types.EmbedContentConfig(
                    output_dimensionality=EMBEDDING_DIMENSION
                ),
            )

            # Keep requests below the 100-per-minute free-tier limit.
            time.sleep(1)

            return response

        except errors.APIError as exc:
            status_code = getattr(exc, "code", None)

            if status_code not in (429, 500, 502, 503, 504):
                raise

            if attempt == max_retries - 1:
                raise

            wait_seconds = 45 * (attempt + 1)

            print(
                f"Gemini API error {status_code}. "
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

def generate_document_embeddings_batch(
    chunks: list[dict],
    batch_size: int = 16,
    api_key: str | None = None,
) -> list[dict]:
    """Generate separate Gemini embeddings for code chunks."""

    if batch_size <= 0:
        raise ValueError("Batch size must be greater than zero.")

    if not chunks:
        return []

    for chunk in chunks:
        if not chunk.get("content", "").strip():
            raise ValueError("Chunk content cannot be empty.")

        if not chunk.get("metadata", {}).get("file_path"):
            raise ValueError("Chunk file_path metadata is missing.")

    client = create_gemini_client(api_key)

    prepared_chunks = [
        prepare_code_document(
            content=chunk["content"],
            title=chunk["metadata"]["file_path"],
        )
        for chunk in chunks
    ]

    batches = split_into_batches(
        prepared_chunks,
        batch_size,
    )

    embedded_chunks = []
    chunk_offset = 0

    for batch in batches:

        contents = [
            types.Content(
                parts=[
                    types.Part.from_text(text=text)
                ]
            )
            for text in batch
        ]
        response = embed_content_with_retry(
    client=client,
    contents=contents,
   )

        if not response.embeddings:
            raise ValueError("Gemini returned no batch embeddings.")

        if len(response.embeddings) != len(batch):
            raise ValueError(
                "Embedding count does not match batch size."
            )

        for embedding in response.embeddings:

            if not embedding.values:
                raise ValueError("Gemini returned an empty embedding.")

            if len(embedding.values) != EMBEDDING_DIMENSION:
                raise ValueError("Unexpected embedding dimensions.")

            original_chunk = chunks[chunk_offset]

            embedded_chunks.append({
                **original_chunk,
                "embedding": [
                    float(value) for value in embedding.values
                ],
                "embedding_model": MODEL_NAME,
            })

            chunk_offset += 1

    return embedded_chunks
