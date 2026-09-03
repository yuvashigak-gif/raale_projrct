import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import HumanReview, DecisionRequest, FinalDecision, AuditLog
from app.schemas import HumanReviewAction

router = APIRouter(prefix="/api/human-review", tags=["Human Review"])

@router.get("")
def get_human_reviews(db: Session = Depends(get_db)):
    reviews = db.query(HumanReview).order_by(HumanReview.timestamp.desc()).all()
    res = []
    for r in reviews:
        req = db.query(DecisionRequest).filter(DecisionRequest.request_id == r.request_id).first()
        res.append({
            "id": r.id,
            "review_id": r.review_id,
            "request_id": r.request_id,
            "risk_level": r.risk_level,
            "model_decisions": json.loads(r.model_decisions) if r.model_decisions else [],
            "status": r.status,
            "human_decision": r.human_decision,
            "reviewer_name": r.reviewer_name,
            "review_notes": r.review_notes,
            "timestamp": r.timestamp,
            "request_type": req.request_type if req else "Unknown",
            "applicant_id": req.applicant_id if req else "Unknown",
            "description": req.description if req else ""
        })
    return res

@router.post("")
def process_human_review(action_in: HumanReviewAction, db: Session = Depends(get_db)):
    req = db.query(DecisionRequest).filter(DecisionRequest.request_id == action_in.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Decision request not found.")
    
    h_review = db.query(HumanReview).filter(HumanReview.request_id == action_in.request_id).first()
    if not h_review:
        raise HTTPException(status_code=404, detail="No pending human review record found for this request.")
    
    act = action_in.action.upper()
    if act not in ["APPROVE", "REJECT", "REQUEST_MORE_INFO"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be APPROVE, REJECT, or REQUEST_MORE_INFO.")

    # Update Human Review record
    h_review.status = "COMPLETED" if act in ["APPROVE", "REJECT"] else "PENDING_INFO"
    h_review.human_decision = act
    h_review.reviewer_name = action_in.reviewer_name
    h_review.review_notes = action_in.notes
    h_review.timestamp = datetime.utcnow()

    # Update Decision Request status
    if act in ["APPROVE", "REJECT"]:
        req.status = "Completed"
        req.final_decision = act
    else:
        req.status = "More Info Required"
        req.final_decision = "MORE INFO REQUESTED"

    # Update Final Decision entity if exists
    fin = db.query(FinalDecision).filter(FinalDecision.request_id == action_in.request_id).first()
    if fin:
        fin.final_decision = act
        fin.explanation = f"Overridden by human reviewer {action_in.reviewer_name}: {action_in.notes}"
        fin.human_review_required = False

    # Create Audit Log entry for Human Override
    audit_count = db.query(AuditLog).count() + 1
    audit = AuditLog(
        audit_id=f"AUD-{audit_count:04d}",
        request_id=req.request_id,
        timestamp=datetime.utcnow(),
        models_used="Human Reviewer Override",
        model_outputs=h_review.model_decisions,
        policy_used="Human Review Policy",
        scores="N/A (Human Decision)",
        final_decision=act,
        winning_model=f"Human ({action_in.reviewer_name})",
        human_review=True,
        reviewer=action_in.reviewer_name,
        reason=f"Human decision executed: {action_in.notes or 'Approved by reviewer'}"
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Human review decision '{act}' recorded successfully.",
        "request_id": req.request_id,
        "status": req.status,
        "final_decision": req.final_decision
    }
