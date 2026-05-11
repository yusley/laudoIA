from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.process import Process
from app.models.report import Report, ReportSection
from app.models.user import User
from app.schemas.report import ReportGenerateRequest, ReportResponse, ReportUpdateRequest
from app.services.ai_service import OpenRouterGenerationError
from app.services.export_service import build_docx, build_pdf
from app.services.report_service import generate_report_for_process, regenerate_section

router = APIRouter(tags=["reports"])


@router.post(
    "/processes/{process_id}/reports/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_report(
    process_id: int,
    payload: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = (
        db.query(Process)
        .options(joinedload(Process.documents), joinedload(Process.questions))
        .filter(Process.id == process_id, Process.user_id == current_user.id)
        .first()
    )
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")
    try:
        report = await generate_report_for_process(
            db,
            current_user,
            process,
            model=payload.model,
            temperature=payload.temperature,
            extra_instructions=payload.extra_instructions,
        )
    except OpenRouterGenerationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return (
        db.query(Report)
        .options(joinedload(Report.sections))
        .filter(Report.id == report.id)
        .first()
    )


@router.get("/processes/{process_id}/reports", response_model=list[ReportResponse])
def list_reports(
    process_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = db.query(Process).filter(Process.id == process_id, Process.user_id == current_user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")
    return (
        db.query(Report)
        .options(joinedload(Report.sections))
        .filter(Report.process_id == process_id)
        .order_by(Report.created_at.desc())
        .all()
    )


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .join(Process, Process.id == Report.process_id)
        .options(joinedload(Report.sections))
        .filter(Report.id == report_id, Process.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Laudo nao encontrado.")
    return report


@router.put("/reports/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    payload: ReportUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = (
        db.query(Report)
        .join(Process, Process.id == Report.process_id)
        .options(joinedload(Report.sections))
        .filter(Report.id == report_id, Process.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Laudo nao encontrado.")

    report.title = payload.title
    report.content = payload.content
    report.status = payload.status

    for existing in list(report.sections):
        db.delete(existing)

    db.flush()

    for index, section_payload in enumerate(payload.sections, start=1):
        db.add(
            ReportSection(
                report_id=report.id,
                section_order=index,
                title=section_payload.title,
                content=section_payload.content,
            )
        )

    db.add(report)
    db.commit()
    return (
        db.query(Report)
        .options(joinedload(Report.sections))
        .filter(Report.id == report.id)
        .first()
    )


@router.post("/reports/{report_id}/sections/{section_id}/regenerate", response_model=ReportResponse)
async def regenerate_report_section(
    report_id: int,
    section_id: int,
    payload: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = (
        db.query(Report)
        .join(Process, Process.id == Report.process_id)
        .options(joinedload(Report.sections), joinedload(Report.process).joinedload(Process.documents), joinedload(Report.process).joinedload(Process.questions))
        .filter(Report.id == report_id, Process.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Laudo nao encontrado.")

    section = next((item for item in report.sections if item.id == section_id), None)
    if not section:
        raise HTTPException(status_code=404, detail="Secao nao encontrada.")

    try:
        await regenerate_section(
            db,
            current_user,
            report,
            section,
            model=payload.model,
            temperature=payload.temperature,
        )
    except OpenRouterGenerationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return (
        db.query(Report)
        .options(joinedload(Report.sections))
        .filter(Report.id == report.id)
        .first()
    )


@router.get("/reports/{report_id}/export/docx")
def export_report_docx(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = (
        db.query(Report)
        .join(Process, Process.id == Report.process_id)
        .options(joinedload(Report.sections), joinedload(Report.process))
        .filter(Report.id == report_id, Process.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Laudo nao encontrado.")

    content = build_docx(report)
    headers = {"Content-Disposition": f'attachment; filename="laudo-{report_id}.docx"'}
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.get("/reports/{report_id}/export/pdf")
def export_report_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = (
        db.query(Report)
        .join(Process, Process.id == Report.process_id)
        .options(joinedload(Report.sections), joinedload(Report.process))
        .filter(Report.id == report_id, Process.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Laudo nao encontrado.")

    content = build_pdf(report)
    headers = {"Content-Disposition": f'attachment; filename="laudo-{report_id}.pdf"'}
    return Response(content=content, media_type="application/pdf", headers=headers)
