import pytest

from app.services.prompt_builder import build_codebase_question_prompt


def test_build_codebase_question_prompt():
    question = "Where is payment processing implemented?"
    context = """
[S1] payment_service.py:1-5
class PaymentService:
    def process_payment(self):
        pass
"""

    prompt = build_codebase_question_prompt(
        question=question,
        context=context,
    )

    assert question in prompt
    assert "payment_service.py" in prompt
    assert "[S1]" in prompt
    assert "Do not invent files" in prompt


def test_empty_question():
    with pytest.raises(ValueError):
        build_codebase_question_prompt("", "some code")


def test_empty_context():
    with pytest.raises(ValueError):
        build_codebase_question_prompt("Find payment logic", "")