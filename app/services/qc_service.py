"""
QC Service - Inspection lifecycle, sampling, evaluation
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.qc import QCInspection, QCDefect, QCMeasurement
from app.models.inventory import Batch
from app.schemas.qc import InspectionCreate, DefectCreate, MeasurementCreate


class QCService:
    @staticmethod
    def _compute_sampling(lot_size: Optional[int], level: str = "II") -> dict:
        """
        Simplified sampling calculator (MVP).
        - Returns sample_size and basic accept/reject thresholds for major/minor.
        Note: For production, replace with ISO 2859-1 tables.
        """
        if not lot_size or lot_size <= 0:
            return {
                "sample_size": None,
                "accept_maj": 0,
                "reject_maj": 1,
                "accept_min": 3,
                "reject_min": 4,
            }

        # Very rough mapping by lot size buckets
        if lot_size <= 50:
            sample = min(13, lot_size)
        elif lot_size <= 150:
            sample = 20
        elif lot_size <= 500:
            sample = 32
        elif lot_size <= 1200:
            sample = 50
        else:
            sample = 80

        return {
            "sample_size": sample,
            "accept_maj": 0,  # strict by default for MVP
            "reject_maj": 1,
            "accept_min": 3,
            "reject_min": 4,
        }

    @staticmethod
    def create_inspection(db: Session, payload: InspectionCreate, owner_id: Optional[int]) -> QCInspection:
        batch = db.query(Batch).filter(Batch.id == payload.batch_id).first()
        if not batch:
            raise ValueError("Batch không tồn tại")

        sampling = QCService._compute_sampling(payload.lot_size, payload.inspection_level or "II")

        insp = QCInspection(
            type=payload.type,
            batch_id=payload.batch_id,
            lot_size=payload.lot_size,
            inspection_level=payload.inspection_level or "II",
            aql_critical=payload.aql_critical if payload.aql_critical is not None else 0.0,
            aql_major=payload.aql_major if payload.aql_major is not None else 1.5,
            aql_minor=payload.aql_minor if payload.aql_minor is not None else 4.0,
            sample_size=sampling["sample_size"],
            accept_maj=sampling["accept_maj"],
            reject_maj=sampling["reject_maj"],
            accept_min=sampling["accept_min"],
            reject_min=sampling["reject_min"],
            status="in_progress",
            owner_id=owner_id,
            note=payload.note,
            started_at=datetime.utcnow(),
        )
        db.add(insp)
        db.commit()
        db.refresh(insp)
        return insp

    @staticmethod
    def add_defects(db: Session, inspection_id: int, defects: List[DefectCreate]) -> List[QCDefect]:
        insp = db.query(QCInspection).filter(QCInspection.id == inspection_id).first()
        if not insp:
            raise ValueError("Inspection không tồn tại")
        if insp.status not in ("in_progress", "draft"):
            raise ValueError("Inspection đã submit, không thể thêm lỗi")

        created = []
        for d in defects:
            row = QCDefect(
                inspection_id=inspection_id,
                code=d.code,
                name=d.name,
                severity=d.severity,
                qty=d.qty,
                description=d.description,
            )
            db.add(row)
            created.append(row)
        db.commit()
        return created

    @staticmethod
    def add_measurements(db: Session, inspection_id: int, measurements: List[MeasurementCreate]) -> List[QCMeasurement]:
        insp = db.query(QCInspection).filter(QCInspection.id == inspection_id).first()
        if not insp:
            raise ValueError("Inspection không tồn tại")
        if insp.status not in ("in_progress", "draft"):
            raise ValueError("Inspection đã submit, không thể thêm số đo")

        created = []
        for m in measurements:
            row = QCMeasurement(
                inspection_id=inspection_id,
                characteristic=m.characteristic,
                value=m.value,
                unit=m.unit,
                pass_fail=m.pass_fail if m.pass_fail is not None else True,
                method=m.method,
            )
            db.add(row)
            created.append(row)
        db.commit()
        return created

    @staticmethod
    def get_detail(db: Session, inspection_id: int) -> dict:
        insp = db.query(QCInspection).filter(QCInspection.id == inspection_id).first()
        if not insp:
            raise ValueError("Inspection không tồn tại")
        defects = db.query(QCDefect).filter(QCDefect.inspection_id == inspection_id).all()
        measurements = (
            db.query(QCMeasurement).filter(QCMeasurement.inspection_id == inspection_id).all()
        )
        return {"inspection": insp, "defects": defects, "measurements": measurements}

    @staticmethod
    def list(db: Session, batch_id: Optional[int] = None, type_: Optional[str] = None, status: Optional[str] = None):
        q = db.query(QCInspection)
        if batch_id:
            q = q.filter(QCInspection.batch_id == batch_id)
        if type_:
            q = q.filter(QCInspection.type == type_)
        if status:
            q = q.filter(QCInspection.status == status)
        return q.order_by(QCInspection.started_at.desc()).all()

    @staticmethod
    def _evaluate(db: Session, insp: QCInspection) -> str:
        # Aggregate defects by severity
        defects = db.query(QCDefect).filter(QCDefect.inspection_id == insp.id).all()
        total_critical = sum(d.qty for d in defects if d.severity == "critical")
        total_major = sum(d.qty for d in defects if d.severity == "major")
        total_minor = sum(d.qty for d in defects if d.severity == "minor")

        # Rules (MVP):
        if total_critical > 0:
            return "reject"
        if insp.reject_maj is not None and total_major >= insp.reject_maj:
            return "reject"
        # Minor overflow → hold
        if insp.reject_min is not None and total_minor >= insp.reject_min:
            return "hold"
        # Otherwise accept
        return "accept"

    @staticmethod
    def submit(db: Session, inspection_id: int, decision: Optional[str], note: Optional[str]) -> QCInspection:
        insp = db.query(QCInspection).filter(QCInspection.id == inspection_id).first()
        if not insp:
            raise ValueError("Inspection không tồn tại")
        if insp.status not in ("in_progress", "draft"):
            raise ValueError("Inspection đã submit")

        auto_decision = QCService._evaluate(db, insp)
        final_decision = decision or auto_decision

        insp.status = "submitted"
        insp.decision = final_decision
        insp.completed_at = datetime.utcnow()
        if note:
            insp.note = (insp.note + "\n" if insp.note else "") + note

        # Update Batch qc_status
        batch = db.query(Batch).filter(Batch.id == insp.batch_id).first()
        if batch:
            if final_decision == "accept":
                batch.qc_status = "passed"
            elif final_decision == "reject":
                batch.qc_status = "failed"
            else:
                batch.qc_status = "pending"  # hold/rework

        db.commit()
        db.refresh(insp)
        return insp

