from datetime import date, datetime

from pydantic import BaseModel, Field


class ProcessBase(BaseModel):
    process_number: str = Field(..., min_length=3)
    court: str
    labor_court: str
    city: str
    state: str = Field(..., min_length=2, max_length=2)
    claimant: str
    defendant: str
    expert_name: str
    expert_registry: str
    report_type: str
    diligence_date: date | None = None
    diligence_location: str | None = None
    notes: str | None = None


class ProcessCreate(ProcessBase):
    pass


class ProcessUpdate(ProcessBase):
    pass


class ProcessResponse(ProcessBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
