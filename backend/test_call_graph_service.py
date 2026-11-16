
from app.services.call_graph_service import build_call_graph


def test_build_call_graph_resolves_function_and_method_calls():
    file_path = "payment_service.py"

    classes = [
        {
            "name": "PaymentService",
            "qualified_name": "PaymentService",
            "file_path": file_path,
            "line": 1,
        }
    ]

    functions = [
        {
            "name": "validate_amount",
            "qualified_name": "PaymentService.validate_amount",
            "file_path": file_path,
            "line": 2,
        },
        {
            "name": "charge",
            "qualified_name": "PaymentService.charge",
            "file_path": file_path,
            "line": 5,
        },
        {
            "name": "process_payment",
            "qualified_name": "PaymentService.process_payment",
            "file_path": file_path,
            "line": 8,
        },
        {
            "name": "helper",
            "qualified_name": "helper",
            "file_path": file_path,
            "line": 12,
        },
    ]

    calls = [
        {
            "caller": "PaymentService.process_payment",
            "callee": "self.validate_amount",
            "line": 9,
            "file_path": file_path,
        },
        {
            "caller": "PaymentService.process_payment",
            "callee": "self.charge",
            "line": 10,
            "file_path": file_path,
        },
        {
            "caller": "helper",
            "callee": "unknown_function",
            "line": 13,
            "file_path": file_path,
        },
    ]

    graph = build_call_graph(functions, calls, classes)

    assert len(graph["nodes"]) == 4
    assert len(graph["edges"]) == 2
    assert len(graph["unresolved_calls"]) == 1

    assert {
        edge["resolved_callee"]
        for edge in graph["edges"]
    } == {
        "PaymentService.validate_amount",
        "PaymentService.charge",
    }

    assert graph["unresolved_calls"][0]["callee"] == "unknown_function"
    assert (
        graph["unresolved_calls"][0]["resolution_status"]
        == "unresolved"
    )


def test_build_call_graph_resolves_direct_function_call():
    file_path = "main.py"

    functions = [
        {
            "name": "helper",
            "qualified_name": "helper",
            "file_path": file_path,
            "line": 1,
        },
        {
            "name": "main",
            "qualified_name": "main",
            "file_path": file_path,
            "line": 5,
        },
    ]

    calls = [
        {
            "caller": "main",
            "callee": "helper",
            "line": 6,
            "file_path": file_path,
        }
    ]

    graph = build_call_graph(functions, calls, [])

    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["caller"] == "main"
    assert graph["edges"][0]["callee"] == "helper"
    assert graph["edges"][0]["resolved_callee"] == "helper"
    assert graph["edges"][0]["line"] == 6
    assert graph["unresolved_calls"] == []
