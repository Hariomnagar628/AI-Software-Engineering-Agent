
from app.services.code_parser import parse_python_source


source = """
class PaymentService:
    def process_payment(self, amount: float) -> bool:
        self.validate_amount(amount)
        gateway.charge(amount)
        return True

    def validate_amount(self, amount: float):
        return amount > 0


def calculate_total(price, tax):
    return round(price * (1 + tax), 2)
"""

result = parse_python_source(source, "payment_service.py")
calls = result["calls"]

# Check calls inside a class method.
process_calls = [
    call for call in calls
    if call["caller"] == "PaymentService.process_payment"
]

assert any(
    call["callee"] == "self.validate_amount"
    for call in process_calls
)

gateway_call = next(
    call for call in process_calls
    if call["callee"] == "gateway.charge"
)

assert gateway_call["arguments_count"] == 1

# Check a direct function call.
round_call = next(
    call for call in calls
    if call["callee"] == "round"
)

assert round_call["caller"] == "calculate_total"
assert round_call["arguments_count"] == 2

# Check calls inside an argument: outer() and inner().
nested_result = parse_python_source(
    "def example():\n    outer(inner())\n",
    "nested.py",
)

nested_names = [
    call["callee"] for call in nested_result["calls"]
]

assert "outer" in nested_names
assert "inner" in nested_names

print("Function-call extraction tests passed!")
