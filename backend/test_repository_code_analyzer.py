
from app.services.repository_code_analyzer import analyze_python_file


def test_valid_python_file():
    result = analyze_python_file(
        repository_path="/tmp/agent-test-repo",
        relative_file_path="payment_service.py",
    )

    print(result)

    assert result["file_path"] == "payment_service.py"
    assert result["language"] == "python"
    assert result["size_bytes"] > 0

    assert len(result["classes"]) == 1
    assert result["classes"][0]["name"] == "PaymentService"

    method = next(
        function
        for function in result["functions"]
        if function["name"] == "process_payment"
    )

    assert method["qualified_name"] == "PaymentService.process_payment"
    assert method["arguments"] == ["self", "amount"]

    async_function = next(
        function
        for function in result["functions"]
        if function["name"] == "fetch_payment"
    )

    assert async_function["is_async"] is True

    assert any(
        item["module"] == "decimal"
        for item in result["imports"]
    )

    print("Repository code analyzer test passed!")


def test_secret_file_rejected():
    try:
        analyze_python_file(
            repository_path="/tmp/agent-test-repo",
            relative_file_path=".env",
        )
    except ValueError:
        print("Unsafe file rejection test passed!")
    else:
        raise AssertionError("The analyzer accepted a secret file.")


if __name__ == "__main__":
    test_valid_python_file()
    test_secret_file_rejected()
