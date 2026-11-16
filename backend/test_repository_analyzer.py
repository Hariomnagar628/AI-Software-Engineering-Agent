
from app.services.repository_analyzer import analyze_repository

result = analyze_repository("/tmp/agent-test-repo")

print(result)

# Repository file discovery.
assert result["python_files_found"] >= 3

# At least three valid files should be analyzed:
# main.py, payment_service.py, and user_service.py.
assert result["files_analyzed"] >= 2

# Verify classes from different files are collected.
class_names = {
    item["name"] for item in result["classes"]
}

assert "PaymentService" in class_names
assert "UserService" in class_names

# Verify functions and methods are collected.
function_names = {
    item["name"] for item in result["functions"]
}

assert "process_payment" in function_names
assert "get_user" in function_names
assert "validate_user" in function_names

# Every collected item should retain its source file.
assert all(
    item.get("file_path")
    for item in result["classes"]
    + result["functions"]
    + result["imports"]
)

# Invalid syntax should be reported without stopping analysis.
error_paths = {
    item["file_path"] for item in result["errors"]
}

assert "broken.py" in error_paths

# Check that other files were still analyzed.
assert "user_service.py" in result["analyzed_files"]

print("Repository analyzer tests passed!")
