
from app.services.code_parser import parse_python_source

source = '''
class PaymentService:
    """Handles payment operations."""

    def calculate_total(self, price: float, tax: float) -> float:
        """Calculate the final price including tax."""
        return price * (1 + tax)


async def fetch_payment(payment_id: str) -> dict:
    """Fetch a payment by its identifier."""
    return {"id": payment_id}
'''

result = parse_python_source(source, "payment_service.py")

# Test class docstring
payment_class = result["classes"][0]
assert payment_class["name"] == "PaymentService"
assert payment_class["docstring"] == "Handles payment operations."

# Test regular function metadata
calculate = next(
    function
    for function in result["functions"]
    if function["name"] == "calculate_total"
)

assert calculate["docstring"] == "Calculate the final price including tax."
assert calculate["return_type"] == "float"

assert calculate["argument_details"] == [
    {"name": "self", "annotation": None},
    {"name": "price", "annotation": "float"},
    {"name": "tax", "annotation": "float"},
]

# Test asynchronous function metadata
fetch = next(
    function
    for function in result["functions"]
    if function["name"] == "fetch_payment"
)

assert fetch["is_async"] is True
assert fetch["return_type"] == "dict"
assert fetch["docstring"] == "Fetch a payment by its identifier."

print("Code parser metadata tests passed!")
