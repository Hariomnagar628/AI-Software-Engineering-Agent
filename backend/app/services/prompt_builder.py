def build_codebase_question_prompt(
    question: str,
    context: str,
) -> str:
    """
    Build a prompt that instructs Gemini to answer
    using only the retrieved repository context.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not context.strip():
        raise ValueError("Retrieved context cannot be empty")

    return f"""
You are an expert software engineering assistant.

Your task is to answer questions about a software repository.

Follow these rules:

1. Answer using only the provided repository context.
2. Do not invent files, functions, classes, or implementation details.
3. If the context does not contain enough information, clearly say so.
4. Explain technical concepts in simple and clear language.
5. When making a claim about the code, cite its source using
   the provided source labels, such as [S1] or [S2].
6. Do not create source references that were not provided.

REPOSITORY CONTEXT:

{context}

USER QUESTION:

{question}

Provide a clear and structured answer.
"""