"""
MockTest agent: generates a full-length timed exam paper as JSON.
"""
from pathlib import Path

from app.services.openai_service import chat_completion
from app.utils.helper import extract_json_block, safe_json_loads
from app.utils.logger import logger

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
SYSTEM_PROMPT = (PROMPT_DIR / "system_prompt.txt").read_text()
MOCKTEST_TEMPLATE = (PROMPT_DIR / "mocktest_prompt.txt").read_text()


class MockTestAgent:
    def generate_paper(
        self,
        exam_name: str,
        duration_minutes: int,
        subjects: list[str],
        total_questions: int,
    ) -> dict:
        prompt = MOCKTEST_TEMPLATE.format(
            exam_name=exam_name,
            duration_minutes=duration_minutes,
            subjects=", ".join(subjects),
            total_questions=total_questions,
        )

        raw = chat_completion(system_prompt=SYSTEM_PROMPT, user_prompt=prompt, temperature=0.4)
        data = safe_json_loads(extract_json_block(raw))

        if not data or "sections" not in data:
            logger.warning("MockTest agent returned unexpected format, using fallback.")
            data = self._fallback_paper(subjects, total_questions)

        return data

    @staticmethod
    def _fallback_paper(subjects: list[str], total_questions: int) -> dict:
        per_subject = max(total_questions // max(len(subjects), 1), 1)
        return {
            "sections": [
                {
                    "subject": subject,
                    "questions": [
                        {
                            "question": f"Placeholder question {i + 1} for {subject}.",
                            "options": ["A", "B", "C", "D"],
                            "correct_answer": "A",
                            "marks": 1,
                        }
                        for i in range(per_subject)
                    ],
                }
                for subject in subjects
            ]
        }
