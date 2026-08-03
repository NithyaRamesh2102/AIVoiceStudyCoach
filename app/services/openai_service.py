"""
Thin wrapper around the OpenAI client used by every agent.
Centralizing this makes it easy to swap models/providers later.
"""
from openai import OpenAI

from app.config import settings
from app.utils.logger import logger

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY is not set — AI calls will fail.")
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def chat_completion(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    temperature: float = 0.6,
    json_mode: bool = False,
) -> str:
    """
    Calls the chat completion endpoint and returns the raw text content.
    """
    client = get_client()
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(
        model=model or settings.OPENAI_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    return response.choices[0].message.content or ""
