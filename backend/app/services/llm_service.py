import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors


load_dotenv()

MODEL_NAME = "gemini-3.8-flash"

MAX_RETRIES = 3
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def generate_llm_response(
    prompt: str,
    api_key: str | None = None,
) -> str:
    """
    Send a prompt to Gemini and return its generated text.
    Retry temporary API failures.
    """

    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")

    if not resolved_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=resolved_api_key)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2048,
                ),
            )

            answer = response.text

            if not answer:
                raise RuntimeError("Gemini returned an empty response")

            return answer.strip()

        except errors.APIError as exc:
            status_code = getattr(exc, "code", None)

            if status_code not in RETRYABLE_STATUS_CODES:
                raise

            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Gemini is temporarily unavailable after "
                    f"{MAX_RETRIES} attempts. Please try again later."
                ) from exc

            wait_seconds = attempt * 2

            print(
                f"Gemini temporary error ({status_code}). "
                f"Retrying in {wait_seconds} seconds... "
                f"Attempt {attempt}/{MAX_RETRIES}"
            )

            time.sleep(wait_seconds)

    raise RuntimeError("Gemini response generation failed")