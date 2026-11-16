
from app.services.file_dependency_analyzer import (
    build_file_dependency_graph,
)


repository_files = [
    "main.py",
    "payment_service.py",
    "user_service.py",
    "external.py",
]

imports = [
    {
        "module": "user_service",
        "name": "validate_user",
        "alias": None,
        "level": 0,
        "line": 1,
        "file_path": "payment_service.py",
    },
    {
        "module": "payment_service",
        "name": None,
        "alias": None,
        "level": 0,
        "line": 1,
        "file_path": "main.py",
    },
    {
        "module": "fastapi",
        "name": "FastAPI",
        "alias": None,
        "level": 0,
        "line": 1,
        "file_path": "main.py",
    },
]

graph = build_file_dependency_graph(
    repository_files=repository_files,
    imports=imports,
)

assert graph["statistics"]["total_files"] == 4
assert graph["statistics"]["total_dependencies"] == 2
assert graph["statistics"]["unresolved_imports"] == 1

assert {
    (edge["source"], edge["target"])
    for edge in graph["edges"]
} == {
    ("payment_service.py", "user_service.py"),
    ("main.py", "payment_service.py"),
}

assert graph["unresolved_imports"][0]["module"] == "fastapi"

print("File dependency analyzer tests passed!")
