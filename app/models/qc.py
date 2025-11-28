"""
QC Models - Inspection, Defect, Measurement
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class QCInspection(Base):
    __tablename__ = "qc_inspections"

    id = Column(Integer, primary_key=True, index=True)

    # Inspection Info
    type = Column(String(20), nullable=False)  # input|inprocess|output|rcq
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)

    # Sampling / AQL
    lot_size = Column(Integer)
    inspection_level = Column(String(10), default="II")
    aql_critical = Column(Float, default=0.0)
    aql_major = Column(Float, default=1.5)
    aql_minor = Column(Float, default=4.0)
    sample_size = Column(Integer)
    accept_maj = Column(Integer)
    reject_maj = Column(Integer)
    accept_min = Column(Integer)
    reject_min = Column(Integer)

    # Status & Decision
    status = Column(String(20), default="in_progress")  # draft|in_progress|submitted|accepted|hold|rejected
    decision = Column(String(20))  # accept|rework|hold|reject

    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Notes & Timestamps
    note = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    batch = relationship("Batch")
    owner = relationship("User")


class QCDefect(Base):
    __tablename__ = "qc_defects"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("qc_inspections.id"), nullable=False)

    code = Column(String(50))
    name = Column(String(255))
    severity = Column(String(10), nullable=False)  # critical|major|minor
    qty = Column(Integer, default=1)
    description = Column(Text)


class QCMeasurement(Base):
    __tablename__ = "qc_measurements"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("qc_inspections.id"), nullable=False)

    characteristic = Column(String(100), nullable=False)
    value = Column(Float)
    unit = Column(String(20))
    pass_fail = Column(Boolean, default=True)
    method = Column(String(50))

