"""
Quiz agent: generates multiple-choice questions as structured JSON.
"""
from pathlib import Path

from app.services.openai_service import chat_completion
from app.utils.helper import extract_json_block, safe_json_loads
from app.utils.logger import logger

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
SYSTEM_PROMPT = (PROMPT_DIR / "system_prompt.txt").read_text()
QUIZ_TEMPLATE = (PROMPT_DIR / "quiz_prompt.txt").read_text()


class QuizAgent:
    def generate_questions(
        self, subject: str, topic: str, difficulty: str, num_questions: int
    ) -> list[dict]:
        prompt = QUIZ_TEMPLATE.format(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
        )

        raw = chat_completion(system_prompt=SYSTEM_PROMPT, user_prompt=prompt, temperature=0.5)
        parsed = safe_json_loads(extract_json_block(raw), default=[])

        if not isinstance(parsed, list) or not parsed:
            logger.warning("Quiz agent returned unexpected format, using fallback.")
            parsed = self._fallback_questions(subject, num_questions)

        return parsed

    @staticmethod
    def _fallback_questions(subject: str, num_questions: int) -> list[dict]:
        return [
            {
                "question": f"Placeholder question {i + 1} about {subject}. "
                            f"(AI generation unavailable — check OPENAI_API_KEY.)",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": "This is a fallback question.",
            }
            for i in range(num_questions)
        ]
