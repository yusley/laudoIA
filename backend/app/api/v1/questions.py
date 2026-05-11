from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.process import Process
from app.models.question import Question
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionUpdate

router = APIRouter(tags=["questions"])


@router.post(
    "/processes/{process_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_question(
    process_id: int,
    payload: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = db.query(Process).filter(Process.id == process_id, Process.user_id == current_user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")

    question = Question(process_id=process_id, **payload.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.get("/processes/{process_id}/questions", response_model=list[QuestionResponse])
def list_questions(
    process_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = db.query(Process).filter(Process.id == process_id, Process.user_id == current_user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")
    return db.query(Question).filter(Question.process_id == process_id).order_by(Question.created_at.asc()).all()


@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    payload: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = (
        db.query(Question)
        .join(Process, Process.id == Question.process_id)
        .filter(Question.id == question_id, Process.user_id == current_user.id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Quesito nao encontrado.")

    for field, value in payload.model_dump().items():
        setattr(question, field, value)

    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = (
        db.query(Question)
        .join(Process, Process.id == Question.process_id)
        .filter(Question.id == question_id, Process.user_id == current_user.id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Quesito nao encontrado.")
    db.delete(question)
    db.commit()
    return None
