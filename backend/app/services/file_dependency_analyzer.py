
from pathlib import PurePosixPath


def build_file_dependency_graph(
    repository_files: list[str],
    imports: list[dict],
) -> dict:
    """
    Build a file-level graph using Python import statements.

    Nodes represent Python files.
    Edges represent imports between files in the repository.
    """
    python_files = [
        path for path in repository_files
        if path.endswith(".py")
    ]

    nodes = [
        {
            "id": file_path,
            "file_path": file_path,
        }
        for file_path in python_files
    ]

    available_files = set(python_files)
    edges = []
    unresolved_imports = []

    def find_module_file(module_path: str) -> str | None:
        """Find a module or package inside the repository."""
        module_path = module_path.replace(".", "/")

        candidates = [
            f"{module_path}.py",
            f"{module_path}/__init__.py",
        ]

        for candidate in candidates:
            if candidate in available_files:
                return candidate

        return None

    for item in imports:
        source_file = item["file_path"]
        module = item.get("module")
        imported_name = item.get("name")
        level = item.get("level", 0)

        if not module and not imported_name:
            unresolved_imports.append(item)
            continue

        # Resolve simple absolute imports first.
        if level == 0:
            target = find_module_file(module or "")

            # For: from package import module
            if target is None and module and imported_name:
                target = find_module_file(
                    f"{module}.{imported_name}"
                )

        else:
            # Resolve relative imports using the source file's directory.
            source_directory = PurePosixPath(source_file).parent

            # Relative import level 1 means the current package.
            package_parts = list(source_directory.parts)

            # For module files, remove the module filename.
            if not source_file.endswith("/__init__.py"):
                package_parts = package_parts[:-1]

            remove_count = level - 1

            if remove_count > len(package_parts):
                target = None
            else:
                base_parts = package_parts[:len(package_parts) - remove_count]

                if module:
                    base_parts.extend(module.split("."))

                base_module = "/".join(base_parts)

                target = find_module_file(base_module)

                if target is None and imported_name:
                    target = find_module_file(
                        f"{base_module}.{imported_name}"
                    )

        if target is None:
            unresolved_imports.append(item)
            continue

        edges.append({
            "source": source_file,
            "target": target,
            "type": "imports",
            "module": module,
            "imported_name": imported_name,
            "line": item["line"],
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "unresolved_imports": unresolved_imports,
        "statistics": {
            "total_files": len(nodes),
            "total_dependencies": len(edges),
            "unresolved_imports": len(unresolved_imports),
        },
    }
