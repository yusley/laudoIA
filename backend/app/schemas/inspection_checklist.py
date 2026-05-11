from datetime import datetime

from pydantic import BaseModel, Field


class ChecklistAgent(BaseModel):
    enabled: bool = False
    agent_label: str = ""
    agent_type: str | None = None
    nr16_options: list[str] = Field(default_factory=list)
    notes: str | None = None
    exposure_time: str | None = None
    risk_accentuated: str | None = None
    permanence_risk_areas: str | None = None


class InspectionChecklistBase(BaseModel):
    function_role: str | None = None
    has_cleaning_products_contact: str | None = None
    cleaning_products: list[str] = Field(default_factory=list)
    cleaning_products_other: str | None = None
    sector: str | None = None
    activity_description: str | None = None
    agents: list[ChecklistAgent] = Field(default_factory=list)
    epi_supply_notes: str | None = None
    epi_types: list[str] = Field(default_factory=list)
    epi_signed_form: str | None = None
    epi_training: str | None = None
    epi_supervised_use: str | None = None
    documents: list[str] = Field(default_factory=list)
    summary_routine: str | None = None
    summary_exposure: str | None = None
    summary_observations: str | None = None


class InspectionChecklistUpdate(InspectionChecklistBase):
    pass


class InspectionChecklistResponse(InspectionChecklistBase):
    id: int | None = None
    process_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


def build_default_checklist() -> InspectionChecklistBase:
    return InspectionChecklistBase(
        agents=[
            ChecklistAgent(enabled=True, agent_label="Qual agente especifico"),
            ChecklistAgent(enabled=False, agent_label="Segundo agente especifico"),
            ChecklistAgent(enabled=False, agent_label="Terceiro agente especifico"),
            ChecklistAgent(enabled=False, agent_label="Quarto agente especifico"),
        ]
    )
