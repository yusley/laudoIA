from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(ORMBaseModel):
    created_at: datetime
    updated_at: datetime | None = None


class DateMixin(ORMBaseModel):
    diligence_date: date | None = None
