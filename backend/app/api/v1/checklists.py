from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.inspection_checklist import InspectionChecklist
from app.models.process import Process
from app.models.user import User
from app.schemas.inspection_checklist import (
    InspectionChecklistResponse,
    InspectionChecklistUpdate,
    build_default_checklist,
)

router = APIRouter(tags=["checklists"])


def _get_process_or_404(db: Session, current_user: User, process_id: int) -> Process:
    process = db.query(Process).filter(Process.id == process_id, Process.user_id == current_user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")
    return process


@router.get("/processes/{process_id}/checklist", response_model=InspectionChecklistResponse)
def get_checklist(
    process_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = _get_process_or_404(db, current_user, process_id)
    checklist = process.inspection_checklist
    if not checklist:
        default_data = build_default_checklist()
        return InspectionChecklistResponse(process_id=process_id, **default_data.model_dump())
    return InspectionChecklistResponse(process_id=process_id, **checklist.checklist_data, id=checklist.id, created_at=checklist.created_at, updated_at=checklist.updated_at)


@router.put("/processes/{process_id}/checklist", response_model=InspectionChecklistResponse)
def upsert_checklist(
    process_id: int,
    payload: InspectionChecklistUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = _get_process_or_404(db, current_user, process_id)
    checklist = process.inspection_checklist

    if not checklist:
        checklist = InspectionChecklist(process_id=process.id, checklist_data=payload.model_dump())
    else:
        checklist.checklist_data = payload.model_dump()

    db.add(checklist)
    db.commit()
    db.refresh(checklist)
    return InspectionChecklistResponse(
        process_id=process_id,
        **checklist.checklist_data,
        id=checklist.id,
        created_at=checklist.created_at,
        updated_at=checklist.updated_at,
    )
