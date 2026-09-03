from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import AuditLog
from app.schemas import AuditLogResponseItem

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogResponseItem])
def get_audit_logs(
    search: Optional[str] = None,
    decision: Optional[str] = None,
    human_only: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    
    if decision:
        query = query.filter(AuditLog.final_decision == decision.upper())
    if human_only:
        query = query.filter(AuditLog.human_review == True)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (AuditLog.audit_id.like(s)) |
            (AuditLog.request_id.like(s)) |
            (AuditLog.policy_used.like(s)) |
            (AuditLog.reason.like(s)) |
            (AuditLog.reviewer.like(s))
        )
        
    return query.order_by(AuditLog.timestamp.desc()).all()
