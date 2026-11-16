
def build_unified_codebase_graph(analysis: dict) -> dict:
    """
    Combine file dependencies and function dependencies
    into one unified codebase graph.
    """

    nodes = []
    edges = []

    file_graph = analysis["file_dependency_graph"]
    function_graph = analysis["dependency_graph"]

    # 1. Add file nodes.
    for file_node in file_graph["nodes"]:
        nodes.append({
            "id": f'file::{file_node["file_path"]}',
            "name": file_node["file_path"],
            "type": "file",
            "file_path": file_node["file_path"],
        })

    # 2. Add function and method nodes.
    for function_node in function_graph["nodes"]:
        nodes.append({
            **function_node,
            "type": "function",
        })

    # 3. Add file-to-file import edges.
    for edge in file_graph["edges"]:
        edges.append({
            "source": f'file::{edge["source"]}',
            "target": f'file::{edge["target"]}',
            "type": "imports",
            "line": edge["line"],
        })

    # 4. Add file-to-function containment edges.
    for function_node in function_graph["nodes"]:
        edges.append({
            "source": f'file::{function_node["file_path"]}',
            "target": function_node["id"],
            "type": "contains",
        })

    # 5. Add function-to-function call edges.
    for edge in function_graph["edges"]:
        edges.append({
            **edge,
            "type": "calls",
        })

    # 6. Calculate graph statistics.
    edge_counts = {}

    for edge in edges:
        edge_type = edge["type"]
        edge_counts[edge_type] = (
            edge_counts.get(edge_type, 0) + 1
        )

    return {
        "nodes": nodes,
        "edges": edges,
        "statistics": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "file_nodes": sum(
                node["type"] == "file" for node in nodes
            ),
            "function_nodes": sum(
                node["type"] == "function" for node in nodes
            ),
            "edge_counts": edge_counts,
        },
    }
