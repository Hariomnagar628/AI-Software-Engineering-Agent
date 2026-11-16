
from collections import deque


def analyze_function_impact(
    dependency_graph: dict,
    function_name: str,
    file_path: str | None = None,
) -> dict:
    """
    Find direct and indirect callers of a function.

    function_name can be a function's simple name or qualified name.
    Supply file_path when needed to distinguish duplicate names.
    """
    nodes = dependency_graph["nodes"]
    edges = dependency_graph["edges"]

    # Find the function that the user wants to investigate.
    candidates = [
        node for node in nodes
        if (
            node["name"] == function_name
            or node["qualified_name"] == function_name
        )
        and (
            file_path is None
            or node["file_path"] == file_path
        )
    ]

    if not candidates:
        raise ValueError(
            f"Function '{function_name}' was not found in the graph."
        )

    if len(candidates) > 1:
        raise ValueError(
            f"Multiple functions match '{function_name}'. "
            "Use its qualified name and file_path to identify it."
        )

    target = candidates[0]

    # Build a reverse graph: target function -> its callers.
    callers_by_target = {}

    for edge in edges:
        callers_by_target.setdefault(
            edge["target"], []
        ).append(edge["source"])

    # Breadth-first search discovers callers level by level.
    queue = deque([(target["id"], 0)])
    visited = {target["id"]}
    impact_nodes = []

    nodes_by_id = {node["id"]: node for node in nodes}

    while queue:
        current_id, depth = queue.popleft()

        if depth > 0:
            current_node = nodes_by_id[current_id]
            impact_nodes.append({
                "id": current_node["id"],
                "name": current_node["name"],
                "qualified_name": current_node["qualified_name"],
                "file_path": current_node["file_path"],
                "line": current_node["line"],
                "depth": depth,
            })

        for caller_id in callers_by_target.get(current_id, []):
            if caller_id not in visited:
                visited.add(caller_id)
                queue.append((caller_id, depth + 1))

    direct_callers = [
        node for node in impact_nodes
        if node["depth"] == 1
    ]

    indirect_callers = [
        node for node in impact_nodes
        if node["depth"] > 1
    ]

    return {
        "target": target,
        "direct_callers": direct_callers,
        "indirect_callers": indirect_callers,
        "total_affected_functions": len(impact_nodes),
    }
