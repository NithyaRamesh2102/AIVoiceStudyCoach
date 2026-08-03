"""
Tutor agent: holds the conversational Q&A logic for the study tutor.
"""
from pathlib import Path

from app.services.openai_service import chat_completion

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
SYSTEM_PROMPT = (PROMPT_DIR / "system_prompt.txt").read_text()
TUTOR_TEMPLATE = (PROMPT_DIR / "tutor_prompt.txt").read_text()


class TutorAgent:
    def respond(self, message: str, subject: str | None, history: list[dict]) -> str:
        history_text = "\n".join(f"{h['role']}: {h['content']}" for h in history[-10:])
        prompt = TUTOR_TEMPLATE.format(
            subject=subject or "general studies",
            history=history_text or "(no prior messages)",
            message=message,
        )
        return chat_completion(system_prompt=SYSTEM_PROMPT, user_prompt=prompt)
