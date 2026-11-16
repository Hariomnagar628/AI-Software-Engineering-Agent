from app.services.rag_retriever import build_retrieval_context


def test_build_retrieval_context():
    chunks = [
        {
            "chunk_id": "chunk-1",
            "file_path": "payment_service.py",
            "start_line": 1,
            "end_line": 5,
            "content": "class PaymentService:\n    def process_payment(self):\n        pass",
            "similarity_score": 0.91,
        },
        {
            "chunk_id": "chunk-2",
            "file_path": "user_service.py",
            "start_line": 10,
            "end_line": 15,
            "content": "def validate_user(user_id):\n    return bool(user_id)",
            "similarity_score": 0.82,
        },
    ]

    result = build_retrieval_context(chunks)

    assert len(result["sources"]) == 2
    assert "[S1]" in result["context"]
    assert "[S2]" in result["context"]
    assert "payment_service.py" in result["context"]
    assert "user_service.py" in result["context"]

    assert result["sources"][0]["source_id"] == "S1"
    assert result["sources"][0]["start_line"] == 1

    print("\nGenerated context:")
    print(result["context"])

    print("\nSources:")
    print(result["sources"])


def test_context_respects_character_limit():
    chunks = [
        {
            "chunk_id": "chunk-1",
            "file_path": "large_file.py",
            "start_line": 1,
            "end_line": 100,
            "content": "x" * 1000,
            "similarity_score": 0.90,
        }
    ]

    result = build_retrieval_context(
        chunks,
        max_context_chars=100,
    )

    assert len(result["context"]) <= 100