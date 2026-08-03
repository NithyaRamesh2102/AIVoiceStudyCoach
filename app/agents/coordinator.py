"""
Coordinator agent: routes a free-form request to the right specialist
agent. Used by endpoints (like a generic /tutor/ask) that don't already
know which agent should handle the request.
"""
from app.agents.tutor_agent import TutorAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.quiz_agent import QuizAgent
from app.agents.mocktest_agent import MockTestAgent
from app.agents.progress_agent import ProgressAgent

INTENT_KEYWORDS = {
    "planner": ["plan", "schedule", "timetable", "roadmap"],
    "quiz": ["quiz", "practice questions", "test me", "mcq"],
    "mocktest": ["mock test", "full test", "exam simulation"],
    "progress": ["progress", "how am i doing", "stats", "performance"],
}


class Coordinator:
    """
    Extremely lightweight intent router based on keyword matching.
    For production use, this could be replaced with an LLM-based
    classifier, but keyword routing keeps latency and cost low for
    the common case.
    """

    def __init__(self):
        self.tutor = TutorAgent()
        self.planner = PlannerAgent()
        self.quiz = QuizAgent()
        self.mocktest = MockTestAgent()
        self.progress = ProgressAgent()

    def route(self, message: str) -> str:
        lowered = message.lower()
        for intent, keywords in INTENT_KEYWORDS.items():
            if any(kw in lowered for kw in keywords):
                return intent
        return "tutor"
