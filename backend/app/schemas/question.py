from datetime import datetime

from pydantic import BaseModel


class QuestionBase(BaseModel):
    party: str
    question_number: str
    question_text: str
    generated_answer: str | None = None
    manual_answer: str | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(QuestionBase):
    pass


class QuestionResponse(QuestionBase):
    id: int
    process_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
