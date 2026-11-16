
def build_call_graph(
    functions: list[dict],
    calls: list[dict],
    classes: list[dict],
) -> dict:
    """
    Build a basic static call graph from repository analysis metadata.

    The graph only resolves calls when a definition can be identified
    with reasonable confidence. It does not execute repository code.
    """

    def function_key(function: dict) -> tuple:
        return (
            function.get("file_path"),
            function.get("qualified_name"),
            function.get("line"),
        )

    # Index definitions by their name and qualified name.
    functions_by_name: dict[str, list[dict]] = {}
    functions_by_qualified_name: dict[str, list[dict]] = {}

    for function in functions:
        name = function.get("name")
        qualified_name = function.get("qualified_name")

        if name:
            functions_by_name.setdefault(name, []).append(function)

        if qualified_name:
            functions_by_qualified_name.setdefault(
                qualified_name, []
            ).append(function)

    def find_enclosing_class(caller: str, file_path: str):
        """Find the most specific class containing the caller."""
        matches = [
            cls
            for cls in classes
            if cls.get("file_path") == file_path
            and caller.startswith(cls.get("qualified_name", "") + ".")
        ]

        if not matches:
            return None

        return max(
            matches,
            key=lambda cls: len(cls.get("qualified_name", "")),
        )

    def resolve_call(call: dict):
        callee = call.get("callee", "")
        caller = call.get("caller", "")
        file_path = call.get("file_path", "")

        if not callee or callee == "<module>":
            return None

        # Handle self.method() and cls.method().
        if callee.startswith(("self.", "cls.")):
            enclosing_class = find_enclosing_class(caller, file_path)

            if enclosing_class is None:
                return None

            method_name = callee.split(".", 1)[1]

            # Resolve only simple method names in this first version.
            if "." in method_name:
                return None

            target_name = (
                enclosing_class["qualified_name"] + "." + method_name
            )

            candidates = [
                fn
                for fn in functions_by_qualified_name.get(target_name, [])
                if fn.get("file_path") == file_path
            ]

            return candidates[0] if len(candidates) == 1 else None

        # Resolve simple direct calls, preferring definitions in the
        # same file. For a bare name, avoid guessing across files.
        if "." not in callee:
            candidates = [
                fn
                for fn in functions_by_name.get(callee, [])
                if fn.get("file_path") == file_path
            ]

            # Prefer a unique module-level definition for ordinary
            # function calls. Recursion also resolves to that definition.
            module_candidates = [
                fn for fn in candidates
                if "." not in fn.get("qualified_name", "")
            ]

            if len(module_candidates) == 1:
                return module_candidates[0]

            if len(module_candidates) > 1:
                return None

            # Permit a unique nested function target in the same file.
            if len(candidates) == 1:
                return candidates[0]

            return None

        # Resolve an exact qualified name only when unique in this file.
        candidates = [
            fn
            for fn in functions_by_qualified_name.get(callee, [])
            if fn.get("file_path") == file_path
        ]

        return candidates[0] if len(candidates) == 1 else None

    nodes = [
        {
            "id": (
                f"{function.get('file_path', '')}:"
                f"{function.get('qualified_name', '')}:"
                f"{function.get('line', '')}"
            ),
            "name": function.get("name"),
            "qualified_name": function.get("qualified_name"),
            "file_path": function.get("file_path"),
            "line": function.get("line"),
        }
        for function in functions
    ]

    edges = []
    unresolved_calls = []

    for call in calls:
        target = resolve_call(call)

        if target is None:
            unresolved_calls.append({
                **call,
                "resolution_status": "unresolved",
            })
            continue

        edges.append({
            "caller": call.get("caller"),
            "callee": call.get("callee"),
            "resolved_callee": target.get("qualified_name"),
            "caller_file_path": call.get("file_path"),
            "callee_file_path": target.get("file_path"),
            "line": call.get("line"),
            "resolution_status": "resolved",
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "unresolved_calls": unresolved_calls,
    }
