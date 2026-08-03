from pydantic import BaseModel


class QuizGenerateRequest(BaseModel):
    subject: str
    topic: str | None = None
    difficulty: str = "medium"
    num_questions: int = 5


class QuizQuestionOut(BaseModel):
    id: int
    question_text: str
    options: list[str]


class QuizOut(BaseModel):
    id: int
    subject: str
    topic: str | None
    difficulty: str
    questions: list[QuizQuestionOut]


class QuizSubmitAnswer(BaseModel):
    question_id: int
    answer: str


class QuizSubmitRequest(BaseModel):
    answers: list[QuizSubmitAnswer]


class QuizResultOut(BaseModel):
    quiz_id: int
    score: float
    total_questions: int
    correct_count: int
    breakdown: list[dict]
