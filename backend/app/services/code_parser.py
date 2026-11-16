
import ast


def get_docstring(node: ast.AST) -> str | None:
    """Return a class or function's docstring."""
    return ast.get_docstring(node)


def get_annotation(node: ast.expr | None) -> str | None:
    """Convert a type annotation into readable source."""
    if node is None:
        return None
    return ast.unparse(node)


def get_call_name(node: ast.expr) -> str:
    """Extract a readable name from a function-call expression."""
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        return f"{get_call_name(node.value)}.{node.attr}"

    if isinstance(node, ast.Call):
        return get_call_name(node.func)

    return ast.unparse(node)


class PythonCodeParser(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.functions = []
        self.imports = []
        self.calls = []
        self.scope = []

    def visit_ClassDef(self, node: ast.ClassDef):
        qualified_name = ".".join(self.scope + [node.name])

        self.classes.append({
            "name": node.name,
            "qualified_name": qualified_name,
            "line": node.lineno,
            "end_line": node.end_lineno,
            "bases": [ast.unparse(base) for base in node.bases],
            "docstring": get_docstring(node),
        })

        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def _visit_function(self, node, is_async: bool):
        qualified_name = ".".join(self.scope + [node.name])

        all_args = (
            node.args.posonlyargs
            + node.args.args
            + node.args.kwonlyargs
        )

        argument_details = [
            {
                "name": arg.arg,
                "annotation": get_annotation(arg.annotation),
            }
            for arg in all_args
        ]

        if node.args.vararg:
            argument_details.append({
                "name": "*" + node.args.vararg.arg,
                "annotation": get_annotation(node.args.vararg.annotation),
            })

        if node.args.kwarg:
            argument_details.append({
                "name": "**" + node.args.kwarg.arg,
                "annotation": get_annotation(node.args.kwarg.annotation),
            })

        self.functions.append({
            "name": node.name,
            "qualified_name": qualified_name,
            "line": node.lineno,
            "end_line": node.end_lineno,
            "arguments": [arg["name"] for arg in argument_details],
            "argument_details": argument_details,
            "return_type": get_annotation(node.returns),
            "docstring": get_docstring(node),
            "is_async": is_async,
        })

        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_function(node, is_async=True)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append({
                "module": alias.name,
                "alias": alias.asname,
                "line": node.lineno,
            })

    def visit_ImportFrom(self, node: ast.ImportFrom):
        for alias in node.names:
            self.imports.append({
                "module": node.module,
                "name": alias.name,
                "alias": alias.asname,
                "level": node.level,
                "line": node.lineno,
            })

    def visit_Call(self, node: ast.Call):
        caller = ".".join(self.scope) if self.scope else "<module>"

        self.calls.append({
            "caller": caller,
            "callee": get_call_name(node.func),
            "line": node.lineno,
            "arguments_count": len(node.args),
            "keyword_arguments": [
                keyword.arg
                for keyword in node.keywords
                if keyword.arg is not None
            ],
        })

        # Also inspect calls inside arguments, such as foo(bar()).
        self.generic_visit(node)


def parse_python_source(source_code: str, file_path: str) -> dict:
    """Parse Python source without executing it."""
    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError as exc:
        raise ValueError(
            f"Python syntax error in {file_path} "
            f"at line {exc.lineno}: {exc.msg}"
        ) from exc

    parser = PythonCodeParser()
    parser.visit(tree)

    return {
        "file_path": file_path,
        "language": "python",
        "classes": parser.classes,
        "functions": parser.functions,
        "imports": parser.imports,
        "calls": parser.calls,
    }
