from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    process_id: int
    filename: str
    original_filename: str
    file_path: str
    file_type: str
    document_category: str
    extracted_text: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
