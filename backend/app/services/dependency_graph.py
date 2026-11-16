
def build_dependency_graph(analysis: dict) -> dict:
    """
    Build a graph from function definitions and resolved function calls.

    Nodes represent functions.
    Edges represent calls between known functions.
    Unresolved calls are reported separately.
    """
    functions = analysis["functions"]
    resolved_calls = analysis["resolved_calls"]

    nodes = []
    edges = []
    unresolved_calls = []

    # Index function definitions so callers can be matched to nodes.
    node_ids_by_function = {}

    for function in functions:
        node_id = (
            f'{function["file_path"]}::'
            f'{function["qualified_name"]}::'
            f'{function["line"]}'
        )

        node = {
            "id": node_id,
            "name": function["name"],
            "qualified_name": function["qualified_name"],
            "file_path": function["file_path"],
            "line": function["line"],
            "is_async": function.get("is_async", False),
        }

        nodes.append(node)

        key = (
            function["file_path"],
            function["qualified_name"],
        )
        node_ids_by_function.setdefault(key, []).append(node_id)

    for call in resolved_calls:
        if call["resolution_status"] != "resolved":
            unresolved_calls.append(call)
            continue

        caller_key = (
            call["file_path"],
            call["caller"],
        )

        caller_candidates = node_ids_by_function.get(
            caller_key, []
        )

        # Avoid inventing an edge if the caller cannot be identified.
        if len(caller_candidates) != 1:
            unresolved_calls.append({
                **call,
                "resolution_status": "caller_not_identified",
            })
            continue

        target_key = (
            call["target_file"],
            call["target_function"],
        )

        target_candidates = node_ids_by_function.get(
            target_key, []
        )

        # Only create an edge when the target is unambiguous.
        if len(target_candidates) != 1:
            unresolved_calls.append({
                **call,
                "resolution_status": "target_not_identified",
            })
            continue

        edges.append({
            "source": caller_candidates[0],
            "target": target_candidates[0],
            "type": "calls",
            "line": call["line"],
            "callee": call["callee"],
            "file_path": call["file_path"],
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "unresolved_calls": unresolved_calls,
        "statistics": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "unresolved_calls": len(unresolved_calls),
        },
    }
