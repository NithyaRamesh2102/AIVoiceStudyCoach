"""
Planner agent: generates structured, day-by-day study plans as JSON.
"""
import json
from pathlib import Path

from app.services.openai_service import chat_completion
from app.utils.helper import extract_json_block, safe_json_loads
from app.utils.logger import logger

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
SYSTEM_PROMPT = (PROMPT_DIR / "system_prompt.txt").read_text()
PLANNER_TEMPLATE = (PROMPT_DIR / "planner_prompt.txt").read_text()


class PlannerAgent:
    def generate_plan(
        self,
        exam_target: str,
        subjects: list[str],
        days: int,
        daily_minutes: int,
        weak_areas: list[str],
    ) -> dict:
        prompt = PLANNER_TEMPLATE.format(
            exam_target=exam_target,
            subjects=", ".join(subjects),
            days=days,
            daily_minutes=daily_minutes,
            weak_areas=", ".join(weak_areas) if weak_areas else "none specified",
        )

        raw = chat_completion(
            system_prompt=SYSTEM_PROMPT, user_prompt=prompt, json_mode=True, temperature=0.4
        )
        data = safe_json_loads(extract_json_block(raw))

        if not data or "days" not in data:
            logger.warning("Planner agent returned unexpected format, using fallback.")
            data = self._fallback_plan(subjects, days, daily_minutes)

        return data

    @staticmethod
    def _fallback_plan(subjects: list[str], days: int, daily_minutes: int) -> dict:
        """A deterministic plan used if the AI response can't be parsed."""
        per_subject_minutes = max(daily_minutes // max(len(subjects), 1), 15)
        return {
            "title": "Study Plan",
            "days": [
                {
                    "day_offset": d,
                    "tasks": [
                        {
                            "subject": subjects[d % len(subjects)],
                            "topic": "Review + practice",
                            "duration_minutes": per_subject_minutes,
                        }
                    ],
                }
                for d in range(days)
            ],
        }
