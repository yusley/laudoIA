from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.process import Process
from app.models.report import Report
from app.models.user import User
from app.schemas.process import ProcessCreate, ProcessResponse, ProcessUpdate

router = APIRouter(prefix="/processes", tags=["processes"])


@router.get("", response_model=list[ProcessResponse])
def list_processes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Process)
        .filter(Process.user_id == current_user.id)
        .order_by(Process.created_at.desc())
        .all()
    )


@router.post("", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
def create_process(
    payload: ProcessCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = Process(user_id=current_user.id, **payload.model_dump())
    db.add(process)
    db.commit()
    db.refresh(process)
    return process


@router.get("/{process_id}", response_model=ProcessResponse)
def get_process(process_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    process = db.query(Process).filter(Process.id == process_id, Process.user_id == current_user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")
    return process


@router.put("/{process_id}", response_model=ProcessResponse)
def update_process(
    process_id: int,
    payload: ProcessUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = db.query(Process).filter(Process.id == process_id, Process.user_id == current_user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")

    for field, value in payload.model_dump().items():
        setattr(process, field, value)

    db.add(process)
    db.commit()
    db.refresh(process)
    return process


@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_process(
    process_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = db.query(Process).filter(Process.id == process_id, Process.user_id == current_user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")

    db.delete(process)
    db.commit()
    return None
