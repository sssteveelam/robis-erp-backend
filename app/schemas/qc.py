"""
QC Schemas - Inspection, Defect, Measurement
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class InspectionCreate(BaseModel):
    type: str = Field(..., pattern="^(input|inprocess|output|rcq)$")
    batch_id: int
    lot_size: Optional[int] = None
    inspection_level: Optional[str] = Field(default="II")
    aql_critical: Optional[float] = None
    aql_major: Optional[float] = None
    aql_minor: Optional[float] = None
    note: Optional[str] = None


class Inspection(BaseModel):
    id: int
    type: str
    batch_id: int
    lot_size: Optional[int] = None
    inspection_level: Optional[str] = None
    aql_critical: Optional[float] = None
    aql_major: Optional[float] = None
    aql_minor: Optional[float] = None
    sample_size: Optional[int] = None
    status: str
    decision: Optional[str] = None
    owner_id: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True


class DefectCreate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    severity: str = Field(..., pattern="^(critical|major|minor)$")
    qty: int = Field(default=1, ge=1)
    description: Optional[str] = None


class MeasurementCreate(BaseModel):
    characteristic: str
    value: Optional[float] = None
    unit: Optional[str] = None
    pass_fail: Optional[bool] = True
    method: Optional[str] = None


class InspectionDetail(Inspection):
    defects: List[dict] = []
    measurements: List[dict] = []


class SubmitInspectionPayload(BaseModel):
    decision: Optional[str] = Field(None, pattern="^(accept|rework|hold|reject)$")
    note: Optional[str] = None

