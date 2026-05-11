from datetime import datetime

from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    model: str | None = None
    temperature: float = Field(default=0.2, ge=0, le=2)
    extra_instructions: str | None = None


class ReportSectionUpdate(BaseModel):
    title: str
    content: str


class ReportSectionResponse(BaseModel):
    id: int
    section_order: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ReportUpdateRequest(BaseModel):
    title: str
    content: str
    status: str
    sections: list[ReportSectionUpdate] = []


class ReportResponse(BaseModel):
    id: int
    process_id: int
    title: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime | None = None
    sections: list[ReportSectionResponse] = []

    model_config = {"from_attributes": True}


class AIUsageSummary(BaseModel):
    model: str
    is_paid_model: bool
    estimated_cost_credit: float
