"""
Business logic for generating study plans and persisting their tasks.
"""
import datetime as dt

from sqlalchemy.orm import Session

from app.agents.planner_agent import PlannerAgent
from app.models.study_plan import StudyPlan, StudyTask
from app.schemas.planner import PlanGenerateRequest
import json


def generate_plan(db: Session, user_id: int, req: PlanGenerateRequest) -> StudyPlan:
    agent = PlannerAgent()
    plan_data = agent.generate_plan(
        exam_target=req.exam_target,
        subjects=req.subjects,
        days=req.days,
        daily_minutes=req.daily_minutes,
        weak_areas=req.weak_areas or [],
    )

    start_date = dt.datetime.utcnow()
    end_date = start_date + dt.timedelta(days=req.days)

    plan = StudyPlan(
        user_id=user_id,
        title=plan_data.get("title", f"{req.exam_target} Study Plan"),
        exam_target=req.exam_target,
        start_date=start_date,
        end_date=end_date,
        raw_plan_json=json.dumps(plan_data),
    )
    db.add(plan)
    db.flush()

    for day_entry in plan_data.get("days", []):
        day_date = start_date + dt.timedelta(days=int(day_entry.get("day_offset", 0)))
        for task in day_entry.get("tasks", []):
            db.add(
                StudyTask(
                    plan_id=plan.id,
                    day=day_date,
                    subject=task.get("subject", "General"),
                    topic=task.get("topic", ""),
                    duration_minutes=int(task.get("duration_minutes", 30)),
                )
            )

    db.commit()
    db.refresh(plan)
    return plan
