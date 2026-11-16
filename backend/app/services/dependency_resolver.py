
def resolve_function_calls(analysis: dict) -> list[dict]:
    """
    Resolve statically identifiable Python calls to repository definitions.

    Supports:
    - Direct function calls within the same file.
    - Imported functions using 'from module import function'.
    - Calls to methods on 'self' within the same class.
    """
    functions = analysis["functions"]
    calls = analysis["calls"]
    imports = analysis["imports"]

    # Index function definitions by file and name.
    functions_by_file_and_name = {}

    for function in functions:
        key = (function["file_path"], function["name"])
        functions_by_file_and_name.setdefault(key, []).append(function)

    # Index methods by file and qualified name.
    functions_by_file_and_qualified_name = {
        (function["file_path"], function["qualified_name"]): function
        for function in functions
    }

    # Build import mappings for each source file.
    imported_functions = {}

    for item in imports:
        module = item.get("module")
        imported_name = item.get("name")

        # Only handle "from module import function" for now.
        if not module or not imported_name:
            continue

        if item.get("level", 0) != 0:
            # Relative imports will be handled in a later improvement.
            continue

        source_file = item["file_path"]
        local_name = item.get("alias") or imported_name
        module_path = module.replace(".", "/") + ".py"

        imported_functions[(source_file, local_name)] = {
            "module_path": module_path,
            "function_name": imported_name,
        }

    resolved_calls = []

    for call in calls:
        source_file = call["file_path"]
        callee = call["callee"]
        caller = call["caller"]
        target = None

        # Case 1: self.method() inside a class method.
        if callee.startswith("self.") and "." in caller:
            class_name = caller.rsplit(".", 1)[0]
            method_name = callee.removeprefix("self.")
            qualified_name = f"{class_name}.{method_name}"

            target = functions_by_file_and_qualified_name.get(
                (source_file, qualified_name)
            )

        # Case 2: A direct call such as validate_user().
        elif "." not in callee:
            # Prefer a definition in the same file.
            same_file_matches = functions_by_file_and_name.get(
                (source_file, callee), []
            )

            if same_file_matches:
                target = same_file_matches[0]

            # Otherwise, look for an imported function.
            else:
                imported = imported_functions.get(
                    (source_file, callee)
                )

                if imported:
                    module_path = imported["module_path"]
                    target_name = imported["function_name"]

                    candidates = [
                        function
                        for function in functions
                        if function["name"] == target_name
                        and (
                            function["file_path"] == module_path
                            or function["file_path"].endswith(
                                "/" + module_path
                            )
                        )
                    ]

                    if len(candidates) == 1:
                        target = candidates[0]

        # Attach resolution information to every call.
        result = {
            **call,
            "resolution_status": "resolved" if target else "unresolved",
            "target_function": (
                target["qualified_name"] if target else None
            ),
            "target_file": target["file_path"] if target else None,
            "target_line": target["line"] if target else None,
        }

        resolved_calls.append(result)

    return resolved_calls
