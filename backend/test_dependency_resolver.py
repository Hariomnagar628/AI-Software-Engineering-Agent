
from app.services.dependency_resolver import resolve_function_calls


analysis = {
    "functions": [
        {
            "name": "process_payment",
            "qualified_name": "PaymentService.process_payment",
            "file_path": "payment_service.py",
            "line": 3,
        },
        {
            "name": "validate_amount",
            "qualified_name": "PaymentService.validate_amount",
            "file_path": "payment_service.py",
            "line": 8,
        },
        {
            "name": "validate_user",
            "qualified_name": "validate_user",
            "file_path": "user_service.py",
            "line": 1,
        },
    ],
    "imports": [
        {
            "module": "user_service",
            "name": "validate_user",
            "alias": None,
            "level": 0,
            "file_path": "payment_service.py",
        },
    ],
    "calls": [
        {
            "caller": "PaymentService.process_payment",
            "callee": "self.validate_amount",
            "file_path": "payment_service.py",
            "line": 4,
            "arguments_count": 1,
            "keyword_arguments": [],
        },
        {
            "caller": "PaymentService.process_payment",
            "callee": "validate_user",
            "file_path": "payment_service.py",
            "line": 5,
            "arguments_count": 1,
            "keyword_arguments": [],
        },
        {
            "caller": "PaymentService.process_payment",
            "callee": "external_library_call",
            "file_path": "payment_service.py",
            "line": 6,
            "arguments_count": 0,
            "keyword_arguments": [],
        },
    ],
}

results = resolve_function_calls(analysis)

method_call = next(
    call for call in results
    if call["callee"] == "self.validate_amount"
)
assert method_call["resolution_status"] == "resolved"
assert method_call["target_function"] == "PaymentService.validate_amount"
assert method_call["target_file"] == "payment_service.py"
assert method_call["target_line"] == 8

imported_call = next(
    call for call in results
    if call["callee"] == "validate_user"
)
assert imported_call["resolution_status"] == "resolved"
assert imported_call["target_function"] == "validate_user"
assert imported_call["target_file"] == "user_service.py"

unknown_call = next(
    call for call in results
    if call["callee"] == "external_library_call"
)
assert unknown_call["resolution_status"] == "unresolved"
assert unknown_call["target_function"] is None

print("Dependency resolver tests passed!")
