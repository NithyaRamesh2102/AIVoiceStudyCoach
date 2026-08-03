"""
Study plan generation and task management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.study_plan import StudyPlan, StudyTask
from app.models.user import User
from app.schemas.planner import PlanGenerateRequest, StudyPlanOut, TaskUpdateRequest
from app.services.planner_service import generate_plan

router = APIRouter(prefix="/api/planner", tags=["planner"])


@router.post("/generate", response_model=StudyPlanOut)
def generate(
    payload: PlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return generate_plan(db, current_user.id, payload)


@router.get("", response_model=list[StudyPlanOut])
def list_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(StudyPlan)
        .filter(StudyPlan.user_id == current_user.id)
        .order_by(StudyPlan.created_at.desc())
        .all()
    )


@router.get("/{plan_id}", response_model=StudyPlanOut)
def get_plan(plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == plan_id, StudyPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.patch("/tasks/{task_id}")
def update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(StudyTask)
        .join(StudyPlan)
        .filter(StudyTask.id == task_id, StudyPlan.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_completed = payload.is_completed
    db.commit()
    return {"id": task.id, "is_completed": task.is_completed}
