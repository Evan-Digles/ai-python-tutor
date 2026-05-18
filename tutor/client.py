import os
from pathlib import Path

from anthropic import Anthropic, APIConnectionError, APIStatusError, AuthenticationError
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 2048

_client: Anthropic | None = None


class TutorAPIError(Exception):
    pass


def _get_client() -> Anthropic:
    """Return a shared Anthropic client, creating it on first call."""
    global _client
    if _client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise TutorAPIError("ANTHROPIC_API_KEY not set. Add it to your .env file.")
        _client = Anthropic(api_key=key)
    return _client


def chat(system_prompt: str | None, messages: list[dict]) -> tuple[str, int, int]:
    """Call the API with an optional system prompt and message history.

    Pass system_prompt=None to query the raw model with no instructions —
    used by the evaluation script as the "before" baseline.
    Returns (response_text, input_tokens, output_tokens).
    Raises TutorAPIError on any API failure.
    """
    try:
        params: dict = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "messages": messages,
        }
        if system_prompt:
            params["system"] = system_prompt
        response = _get_client().messages.create(**params)
        if not response.content or not hasattr(response.content[0], "text"):
            raise TutorAPIError("Unexpected response format from API.")
        return (
            response.content[0].text,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
    except TutorAPIError:
        raise
    except AuthenticationError:
        raise TutorAPIError("Invalid API key. Check ANTHROPIC_API_KEY in your .env file.")
    except APIConnectionError:
        raise TutorAPIError("Could not connect to the Anthropic API. Check your internet connection.")
    except APIStatusError as e:
        raise TutorAPIError(f"API error {e.status_code}: {e.message}")
