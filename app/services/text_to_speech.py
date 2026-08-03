"""
Text-to-speech service, backed by OpenAI TTS. Writes the generated
audio to the static directory and returns a servable relative URL.
"""
import uuid
from pathlib import Path

from app.config import settings
from app.services.openai_service import get_client
from app.utils.logger import logger

STATIC_AUDIO_DIR = Path("static") / "audio"
STATIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def synthesize_speech(text: str, voice: str = "alloy") -> str:
    """
    Generates speech audio for `text` and returns a relative URL
    (e.g. "/static/audio/<uuid>.mp3") that the frontend can play.
    """
    client = get_client()
    filename = f"{uuid.uuid4().hex}.mp3"
    output_path = STATIC_AUDIO_DIR / filename

    try:
        with client.audio.speech.with_streaming_response.create(
            model=settings.OPENAI_TTS_MODEL,
            voice=voice,
            input=text,
        ) as response:
            response.stream_to_file(output_path)
    except Exception as exc:  # noqa: BLE001
        logger.error("Speech synthesis failed: %s", exc)
        raise

    return f"/static/audio/{filename}"
