
from app.services.code_parser import parse_python_source

source = """
from fastapi import FastAPI

class PaymentService:
    def process_payment(self, amount):
        return amount

async def fetch_payment(payment_id):
    return payment_id
"""

result = parse_python_source(
    source_code=source,
    file_path="app/payment_service.py",
)

print(result)

# Check class extraction.
assert len(result["classes"]) == 1
assert result["classes"][0]["name"] == "PaymentService"
assert result["classes"][0]["line"] == 4

# Check method extraction.
method = next(
    item for item in result["functions"]
    if item["name"] == "process_payment"
)

assert method["qualified_name"] == "PaymentService.process_payment"
assert method["arguments"] == ["self", "amount"]
assert method["line"] == 5

# Check async function extraction.
async_function = next(
    item for item in result["functions"]
    if item["name"] == "fetch_payment"
)

assert async_function["is_async"] is True
assert async_function["arguments"] == ["payment_id"]

# Check imports.
assert any(
    item["module"] == "fastapi"
    and item["name"] == "FastAPI"
    for item in result["imports"]
)

print("Python code parser tests passed!")


try:
    parse_python_source(
        source_code="def broken(:\n    pass",
        file_path="broken.py",
    )
except ValueError as exc:
    assert "syntax error" in str(exc).lower()
    print("Invalid syntax test passed!")
else:
    raise AssertionError("Invalid Python syntax was accepted.")