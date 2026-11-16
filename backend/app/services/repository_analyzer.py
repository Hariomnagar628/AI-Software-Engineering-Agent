
from app.services.file_scanner import scan_repository
from app.services.repository_code_analyzer import analyze_python_file
from app.services.call_graph_service import build_call_graph
from app.services.dependency_resolver import resolve_function_calls
from app.services.dependency_graph import build_dependency_graph
from app.services.file_dependency_analyzer import (
    build_file_dependency_graph,
)
from app.services.unified_graph_builder import (
    build_unified_codebase_graph,
)

def analyze_repository(repository_path: str) -> dict:
    files = scan_repository(repository_path)
    python_files = [
        path for path in files
        if path.lower().endswith(".py")
    ]

    analyzed_files = []
    all_classes = []
    all_functions = []
    all_imports = []
    all_calls = []
    errors = []

    for file_path in python_files:
        try:
            result = analyze_python_file(
                repository_path=repository_path,
                relative_file_path=file_path,
            )

            analyzed_files.append(file_path)

            for item in result["classes"]:
                all_classes.append({
                    **item,
                    "file_path": file_path,
                })

            for item in result["functions"]:
                all_functions.append({
                    **item,
                    "file_path": file_path,
                })

            for item in result["imports"]:
                all_imports.append({
                    **item,
                    "file_path": file_path,
                })

            for item in result["calls"]:
                all_calls.append({
                    **item,
                    "file_path": file_path,
                })

        except ValueError as exc:
            errors.append({
                "file_path": file_path,
                "error": str(exc),
            })

        call_graph = build_call_graph(
        functions=all_functions,
        calls=all_calls,
        classes=all_classes,
    )

       
    
    
    
    analysis = {
        "repository_path": repository_path,
        "python_files_found": len(python_files),
        "files_analyzed": len(analyzed_files),
        "analyzed_files": analyzed_files,
        "classes": all_classes,
        "functions": all_functions,
        "imports": all_imports,
        "calls": all_calls,
        "errors": errors,
    }

    analysis["resolved_calls"] = resolve_function_calls(analysis)

    analysis["dependency_graph"] = build_dependency_graph(
        analysis
    )

    analysis["file_dependency_graph"] = build_file_dependency_graph(
        repository_files=files,
        imports=all_imports,
    )

    analysis["unified_graph"] = build_unified_codebase_graph(
        analysis
    )

    return analysis

