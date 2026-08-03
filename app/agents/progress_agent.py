"""
Progress agent: turns raw analytics into a short natural-language
coaching summary (e.g. for the dashboard or a voice briefing).
"""
from pathlib import Path

from app.services.openai_service import chat_completion

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
SYSTEM_PROMPT = (PROMPT_DIR / "system_prompt.txt").read_text()


class ProgressAgent:
    def summarize(self, summary: dict) -> str:
        prompt = (
            "Summarize this student's study progress in 2-3 encouraging "
            "sentences suitable for a voice briefing. Mention one concrete "
            "suggestion for what to focus on next.\n\n"
            f"Data: {summary}"
        )
        return chat_completion(system_prompt=SYSTEM_PROMPT, user_prompt=prompt, temperature=0.6)
