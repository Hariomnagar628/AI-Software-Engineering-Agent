
from app.services.unified_graph_builder import (
    build_unified_codebase_graph,
)


analysis = {
    "file_dependency_graph": {
        "nodes": [
            {"file_path": "main.py"},
            {"file_path": "payment_service.py"},
        ],
        "edges": [
            {
                "source": "main.py",
                "target": "payment_service.py",
                "line": 1,
            }
        ],
    },
    "dependency_graph": {
        "nodes": [
            {
                "id": "payment_service.py::process_payment::3",
                "name": "process_payment",
                "qualified_name": "process_payment",
                "file_path": "payment_service.py",
                "line": 3,
            },
            {
                "id": "payment_service.py::validate_payment::8",
                "name": "validate_payment",
                "qualified_name": "validate_payment",
                "file_path": "payment_service.py",
                "line": 8,
            },
        ],
        "edges": [
            {
                "source": "payment_service.py::process_payment::3",
                "target": "payment_service.py::validate_payment::8",
                "line": 4,
            }
        ],
    },
}

graph = build_unified_codebase_graph(analysis)

assert graph["statistics"]["total_nodes"] == 4
assert graph["statistics"]["total_edges"] == 4

assert graph["statistics"]["file_nodes"] == 2
assert graph["statistics"]["function_nodes"] == 2

assert graph["statistics"]["edge_counts"] == {
    "imports": 1,
    "contains": 2,
    "calls": 1,
}

edge_types = {edge["type"] for edge in graph["edges"]}

assert edge_types == {"imports", "contains", "calls"}

print("Unified graph tests passed!")
