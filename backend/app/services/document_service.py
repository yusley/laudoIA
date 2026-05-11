import uuid
from pathlib import Path

import docx
import fitz
from fastapi import UploadFile
from io import BytesIO
from PIL import Image

from app.services.ai_service import transcribe_image_checklist


async def build_upload_metadata(process_id: int, file: UploadFile) -> tuple[str, str, bytes]:
    extension = Path(file.filename or "").suffix.lower()
    generated_name = f"{uuid.uuid4().hex}{extension}"
    content = await file.read()
    pseudo_path = f"transient://processes/{process_id}/{generated_name}"
    return generated_name, pseudo_path, content


async def extract_text_from_bytes(content: bytes, original_filename: str, file_type: str) -> str:
    extension = Path(original_filename).suffix.lower()

    if extension == ".txt":
        return content.decode("utf-8", errors="ignore")

    if extension == ".docx":
        document = docx.Document(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())

    if extension == ".pdf":
        texts: list[str] = []
        with fitz.open(stream=content, filetype="pdf") as pdf:
            for page in pdf:
                texts.append(page.get_text("text"))
        return "\n".join(texts).strip()

    if extension in {".png", ".jpg", ".jpeg", ".webp"}:
        ai_transcription = await transcribe_image_checklist(
            image_bytes=content,
            mime_type=file_type,
            filename=original_filename,
        )
        with Image.open(BytesIO(content)) as image:
            return (
                f"[Imagem anexada: {image.width}x{image.height}.]\n"
                f"{ai_transcription}"
            )

    return f"[Extracao de texto nao suportada para {file_type}.]"
