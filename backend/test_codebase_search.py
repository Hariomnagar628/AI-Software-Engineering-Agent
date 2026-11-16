
from app.services.codebase_search import search_codebase


REPOSITORY_PATH = "/tmp/agent-test-repo"

# Search for an existing class/function keyword.
result = search_codebase(
    repository_path=REPOSITORY_PATH,
    query="PaymentService process_payment",
    limit=10,
)

assert result["total_files_searched"] > 0

assert result["total_matching_files"] > 0

payment_result = next(
    (
        item for item in result["results"]
        if item["file_path"] == "payment_service.py"
    ),
    None,
)

assert payment_result is not None
assert "paymentservice" in payment_result["matched_terms"]
assert "process_payment" in payment_result["matched_terms"]

assert payment_result["score"] > 0
assert len(payment_result["matching_lines"]) > 0

# Check empty query handling.
try:
    search_codebase(
        repository_path=REPOSITORY_PATH,
        query="!!!",
    )
except ValueError:
    pass
else:
    raise AssertionError("Empty searchable query should fail.")

# Check invalid limit.
try:
    search_codebase(
        repository_path=REPOSITORY_PATH,
        query="payment",
        limit=100,
    )
except ValueError:
    pass
else:
    raise AssertionError("Invalid limit should fail.")

print("Codebase search tests passed!")

