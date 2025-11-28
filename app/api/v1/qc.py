"""
QC (Quality Control) API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.schemas.inventory import QCCheckpoint, QCCheckpointCreate
from app.schemas.qc import (
    InspectionCreate,
    Inspection,
    InspectionDetail,
    DefectCreate,
    MeasurementCreate,
    SubmitInspectionPayload,
)
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.models.user import User as UserModel
from app.models.inventory import QCCheckpoint as QCCheckpointModel
from app.services.qc_service import QCService

router = APIRouter(prefix="/qc", tags=["QC - Quality Control"]) 


# ============== NEW: QC Inspection Endpoints ==============

@router.post(
    "/inspections",
    response_model=Inspection,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("qc:perform")],
)
def create_inspection(
    payload: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        insp = QCService.create_inspection(db, payload, owner_id=current_user.id)
        return insp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/inspections",
    response_model=list[Inspection],
    dependencies=[require_permission("qc:perform")],
)
def list_inspections(
    batch_id: Optional[int] = Query(default=None),
    type: Optional[str] = Query(default=None, pattern="^(input|inprocess|output|rcq)$"),
    status_: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    items = QCService.list(db, batch_id=batch_id, type_=type, status=status_)
    return items


@router.get(
    "/inspections/{inspection_id}",
    response_model=InspectionDetail,
    dependencies=[require_permission("qc:perform")],
)
def get_inspection_detail(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        data = QCService.get_detail(db, inspection_id)
        insp = data["inspection"]
        defects = data["defects"]
        measurements = data["measurements"]
        return {
            "id": insp.id,
            "type": insp.type,
            "batch_id": insp.batch_id,
            "lot_size": insp.lot_size,
            "inspection_level": insp.inspection_level,
            "aql_critical": insp.aql_critical,
            "aql_major": insp.aql_major,
            "aql_minor": insp.aql_minor,
            "sample_size": insp.sample_size,
            "status": insp.status,
            "decision": insp.decision,
            "owner_id": insp.owner_id,
            "started_at": insp.started_at,
            "completed_at": insp.completed_at,
            "note": insp.note,
            "defects": [
                {
                    "id": d.id,
                    "code": d.code,
                    "name": d.name,
                    "severity": d.severity,
                    "qty": d.qty,
                    "description": d.description,
                }
                for d in defects
            ],
            "measurements": [
                {
                    "id": m.id,
                    "characteristic": m.characteristic,
                    "value": m.value,
                    "unit": m.unit,
                    "pass_fail": m.pass_fail,
                    "method": m.method,
                }
                for m in measurements
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/inspections/{inspection_id}/defects",
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("qc:perform")],
)
def add_defects(
    inspection_id: int,
    defects: List[DefectCreate],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        created = QCService.add_defects(db, inspection_id, defects)
        return {"created": len(created)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/inspections/{inspection_id}/measurements",
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("qc:perform")],
)
def add_measurements(
    inspection_id: int,
    measurements: List[MeasurementCreate],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        created = QCService.add_measurements(db, inspection_id, measurements)
        return {"created": len(created)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/inspections/{inspection_id}/submit",
    response_model=Inspection,
    dependencies=[require_permission("qc:perform")],
)
def submit_inspection(
    inspection_id: int,
    body: SubmitInspectionPayload,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        insp = QCService.submit(db, inspection_id, body.decision, body.note)
        return insp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/checkpoints",
    response_model=QCCheckpoint,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("qc:perform")],
)
def create_qc_checkpoint(
    checkpoint: QCCheckpointCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Tạo QC checkpoint mới

    Permission: qc:perform
    Roles: QC_STAFF, ADMIN

    Checkpoint Types:
    - INPUT: Kiểm đầu vào (nguyên liệu)
    - INPROCESS: Kiểm trong quá trình
    - OUTPUT: Kiểm đầu ra (thành phẩm)
    """
    db_checkpoint = QCCheckpointModel(
        checkpoint_type=checkpoint.checkpoint_type,
        batch_id=checkpoint.batch_id,
        status=checkpoint.status,
        score=checkpoint.score,
        note=checkpoint.note,
        defect_count=checkpoint.defect_count,
        defect_description=checkpoint.defect_description,
        inspector_id=current_user.id,
    )

    db.add(db_checkpoint)

    # Auto-update batch QC status if checkpoint is OUTPUT
    if checkpoint.checkpoint_type == "output":
        from app.models.inventory import Batch

        batch = db.query(Batch).filter(Batch.id == checkpoint.batch_id).first()
        if batch:
            batch.qc_status = checkpoint.status
            batch.qc_note = f"QC Score: {checkpoint.score}/100"

    db.commit()
    db.refresh(db_checkpoint)

    return db_checkpoint


@router.get(
    "/checkpoints",
    response_model=list[QCCheckpoint],
    dependencies=[require_permission("qc:perform")],
)
def get_qc_checkpoints(
    batch_id: Optional[int] = Query(default=None),
    checkpoint_type: Optional[str] = Query(
        default=None, pattern="^(input|inprocess|output)$"
    ),
    status: Optional[str] = Query(default=None, pattern="^(pending|passed|failed)$"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy danh sách QC checkpoints

    Permission: qc:perform
    """
    query = db.query(QCCheckpointModel)

    if batch_id:
        query = query.filter(QCCheckpointModel.batch_id == batch_id)
    if checkpoint_type:
        query = query.filter(QCCheckpointModel.checkpoint_type == checkpoint_type)
    if status:
        query = query.filter(QCCheckpointModel.status == status)

    return query.order_by(QCCheckpointModel.inspected_at.desc()).all()


@router.get(
    "/checkpoints/{checkpoint_id}",
    response_model=QCCheckpoint,
    dependencies=[require_permission("qc:perform")],
)
def get_qc_checkpoint(
    checkpoint_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy chi tiết QC checkpoint"""
    checkpoint = (
        db.query(QCCheckpointModel)
        .filter(QCCheckpointModel.id == checkpoint_id)
        .first()
    )

    if not checkpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QC Checkpoint với ID {checkpoint_id} không tồn tại",
        )

    return checkpoint
