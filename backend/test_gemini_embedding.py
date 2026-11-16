
from app.services.embedding_service import (
    generate_document_embedding,
    generate_query_embedding,
    cosine_similarity,
)


code = """
def validate_user_permission(user_id):
    return user_id in authorized_users
"""

question = "Where does the application check user permissions?"

document_vector = generate_document_embedding(
    content=code,
    title="user_service.py",
)

query_vector = generate_query_embedding(question)

assert len(document_vector) > 0
assert len(query_vector) > 0

assert len(document_vector) == len(query_vector)

similarity = cosine_similarity(
    query_vector,
    document_vector,
)

print("Gemini embedding integration test passed!")
print("Embedding dimensions:", len(document_vector))
print("Similarity score:", round(similarity, 4))

