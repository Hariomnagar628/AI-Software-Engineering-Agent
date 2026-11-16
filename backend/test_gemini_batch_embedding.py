
from app.services.code_chunker import chunk_source_code
from app.services.embedding_service import (
    generate_document_embeddings_batch,
)


source_code = """
def validate_user(user_id):
    return bool(user_id)


def process_payment(user_id, amount):
    if validate_user(user_id):
        return amount
    return 0


def calculate_tax(amount):
    return amount * 0.18
"""

chunks = chunk_source_code(
    content=source_code,
    file_path="payment_service.py",
    chunk_size=150,
    overlap=30,
)

embedded_chunks = generate_document_embeddings_batch(
    chunks=chunks,
    batch_size=2,
)

assert len(embedded_chunks) == len(chunks)

for chunk in embedded_chunks:
    assert chunk["id"]
    assert chunk["content"]
    assert chunk["metadata"]["file_path"] == "payment_service.py"
    assert chunk["embedding"]
    assert chunk["embedding_model"] == "gemini-embedding-2"

dimensions = {
    len(chunk["embedding"])
    for chunk in embedded_chunks
}

assert len(dimensions) == 1

print("Gemini batch embedding integration test passed!")
print("Chunks:", len(embedded_chunks))
print("Embedding dimensions:", dimensions.pop())
