from sqlalchemy.orm import Session

from app.services.rag_retriever import retrieve_code_context
from app.services.prompt_builder import build_codebase_question_prompt
from app.services.llm_service import generate_llm_response


def ask_codebase_question(
    db: Session,
    repository_path: str,
    question: str,
    limit: int = 5,
) -> dict:
    """
    Retrieve relevant code and ask Gemini to answer
    a question about the repository.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty")

    # Step 1: Retrieve relevant code from the repository.
    retrieval = retrieve_code_context(
        db=db,
        repository_path=repository_path,
        query=question,
        limit=limit,
    )

    if not retrieval["context"].strip():
        return {
            "repository_path": repository_path,
            "question": question,
            "answer": (
                "I could not find relevant code in the indexed "
                "repository to answer this question."
            ),
            "sources": [],
            "total_sources": 0,
        }

    # Step 2: Build a prompt using the retrieved context.
    prompt = build_codebase_question_prompt(
        question=question,
        context=retrieval["context"],
    )

    # Step 3: Ask Gemini to generate an answer.
    answer = generate_llm_response(prompt)

    # Step 4: Return the answer with its source references.
    return {
        "repository_path": repository_path,
        "question": question,
        "answer": answer,
        "sources": retrieval["sources"],
        "total_sources": retrieval["total_sources"],
    }