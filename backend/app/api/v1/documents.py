from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.process import Process
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_service import build_upload_metadata, extract_text_from_bytes

router = APIRouter(tags=["documents"])


@router.post(
    "/processes/{process_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    process_id: int,
    document_category: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = db.query(Process).filter(Process.id == process_id, Process.user_id == current_user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")

    filename, file_path, content = await build_upload_metadata(process_id, file)
    extracted_text = await extract_text_from_bytes(
        content,
        file.filename or filename,
        file.content_type or "application/octet-stream",
    )

    document = Document(
        process_id=process_id,
        filename=filename,
        original_filename=file.filename or filename,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        document_category=document_category,
        extracted_text=extracted_text,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/processes/{process_id}/documents", response_model=list[DocumentResponse])
def list_documents(
    process_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process = db.query(Process).filter(Process.id == process_id, Process.user_id == current_user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado.")
    return db.query(Document).filter(Document.process_id == process_id).order_by(Document.created_at.desc()).all()


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = (
        db.query(Document)
        .join(Process, Process.id == Document.process_id)
        .filter(Document.id == document_id, Process.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.")
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .join(Process, Process.id == Document.process_id)
        .filter(Document.id == document_id, Process.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.")
    db.delete(document)
    db.commit()
    return None
