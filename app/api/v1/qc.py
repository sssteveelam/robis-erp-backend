"""
QC (Quality Control) API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.inventory import QCCheckpoint, QCCheckpointCreate
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.models.user import User as UserModel
from app.models.inventory import QCCheckpoint as QCCheckpointModel

router = APIRouter(prefix="/qc", tags=["QC - Quality Control"])


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
