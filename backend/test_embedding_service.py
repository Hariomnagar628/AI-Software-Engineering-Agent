
from app.services.embedding_service import (
    prepare_code_document,
    prepare_code_query,
    cosine_similarity,
)


# Test document preparation.
document = prepare_code_document(
    content="def validate_user(user_id): return bool(user_id)",
    title="user_service.py",
)

assert "user_service.py" in document
assert "validate_user" in document

# Test query preparation.
query = prepare_code_query(
    "Where is user validation implemented?"
)

assert query.startswith("task: code retrieval | query:")

# Test cosine similarity.
vector_a = [1.0, 0.0, 0.0]
vector_b = [1.0, 0.0, 0.0]
vector_c = [0.0, 1.0, 0.0]

assert abs(cosine_similarity(vector_a, vector_b) - 1.0) < 0.000001
assert abs(cosine_similarity(vector_a, vector_c)) < 0.000001

# Test invalid dimensions.
try:
    cosine_similarity([1.0, 2.0], [1.0])
except ValueError:
    pass
else:
    raise AssertionError("Different dimensions should fail.")

# Test zero vectors.
try:
    cosine_similarity([0.0, 0.0], [1.0, 2.0])
except ValueError:
    pass
else:
    raise AssertionError("Zero vectors should fail.")

print("Embedding service offline tests passed!")
