
from app.services.dependency_graph import build_dependency_graph


analysis = {
    "functions": [
        {
            "name": "process_payment",
            "qualified_name": "PaymentService.process_payment",
            "file_path": "payment_service.py",
            "line": 3,
            "is_async": False,
        },
        {
            "name": "validate_amount",
            "qualified_name": "PaymentService.validate_amount",
            "file_path": "payment_service.py",
            "line": 8,
            "is_async": False,
        },
    ],
    "resolved_calls": [
        {
            "caller": "PaymentService.process_payment",
            "callee": "self.validate_amount",
            "file_path": "payment_service.py",
            "line": 4,
            "resolution_status": "resolved",
            "target_function": "PaymentService.validate_amount",
            "target_file": "payment_service.py",
            "target_line": 8,
        },
        {
            "caller": "PaymentService.process_payment",
            "callee": "external_call",
            "file_path": "payment_service.py",
            "line": 5,
            "resolution_status": "unresolved",
            "target_function": None,
            "target_file": None,
            "target_line": None,
        },
    ],
}

graph = build_dependency_graph(analysis)

assert graph["statistics"]["total_nodes"] == 2
assert graph["statistics"]["total_edges"] == 1
assert graph["statistics"]["unresolved_calls"] == 1

edge = graph["edges"][0]

assert edge["type"] == "calls"
assert edge["callee"] == "self.validate_amount"

source_node = next(
    node for node in graph["nodes"]
    if node["id"] == edge["source"]
)

target_node = next(
    node for node in graph["nodes"]
    if node["id"] == edge["target"]
)

assert source_node["qualified_name"] == (
    "PaymentService.process_payment"
)
assert target_node["qualified_name"] == (
    "PaymentService.validate_amount"
)

print("Dependency graph tests passed!")
