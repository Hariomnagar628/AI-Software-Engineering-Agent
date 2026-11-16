
from app.services.impact_analyzer import analyze_function_impact


nodes = [
    {
        "id": "payment.py::validate_amount::1",
        "name": "validate_amount",
        "qualified_name": "validate_amount",
        "file_path": "payment.py",
        "line": 1,
    },
    {
        "id": "payment.py::process_payment::5",
        "name": "process_payment",
        "qualified_name": "process_payment",
        "file_path": "payment.py",
        "line": 5,
    },
    {
        "id": "checkout.py::checkout::10",
        "name": "checkout",
        "qualified_name": "checkout",
        "file_path": "checkout.py",
        "line": 10,
    },
    {
        "id": "main.py::main::20",
        "name": "main",
        "qualified_name": "main",
        "file_path": "main.py",
        "line": 20,
    },
]

graph = {
    "nodes": nodes,
    "edges": [
        {
            "source": "payment.py::process_payment::5",
            "target": "payment.py::validate_amount::1",
        },
        {
            "source": "checkout.py::checkout::10",
            "target": "payment.py::process_payment::5",
        },
        {
            "source": "main.py::main::20",
            "target": "checkout.py::checkout::10",
        },
    ],
}

result = analyze_function_impact(graph, "validate_amount")

assert result["target"]["name"] == "validate_amount"

assert [
    node["name"] for node in result["direct_callers"]
] == ["process_payment"]

assert {
    node["name"] for node in result["indirect_callers"]
} == {"checkout", "main"}

assert result["total_affected_functions"] == 3

assert next(
    node for node in result["indirect_callers"]
    if node["name"] == "checkout"
)["depth"] == 2

assert next(
    node for node in result["indirect_callers"]
    if node["name"] == "main"
)["depth"] == 3

print("Impact analyzer tests passed!")
