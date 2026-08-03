"""
Speech-to-text (transcription) service, backed by OpenAI Whisper.
"""
from pathlib import Path

from app.config import settings
from app.services.openai_service import get_client
from app.utils.logger import logger


def transcribe_audio(file_path: str | Path) -> str:
    """
    Transcribes an audio file on disk and returns the text.
    """
    client = get_client()
    path = Path(file_path)

    with open(path, "rb") as audio_file:
        try:
            result = client.audio.transcriptions.create(
                model=settings.OPENAI_STT_MODEL,
                file=audio_file,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Transcription failed: %s", exc)
            raise
    return result.text
