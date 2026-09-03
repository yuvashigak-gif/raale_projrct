import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import DecisionRequest, ModelResponse, AIModel, ArbitrationPolicy, FinalDecision, AuditLog, HumanReview
from app.schemas import DecisionRequestCreate, DecisionRequestResponse, FinalDecisionResult, RunArbitrationPayload
from app.simulator import generate_model_responses
from app.arbitration_engine import evaluate_arbitration

router = APIRouter(tags=["Decisions & Arbitration"])

@router.get("/api/decisions")
def get_decisions(
    search: Optional[str] = None,
    risk: Optional[str] = None,
    decision: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DecisionRequest)
    
    if risk:
        query = query.filter(DecisionRequest.risk_level == risk.upper())
    if decision:
        query = query.filter(DecisionRequest.final_decision == decision.upper())
    if status_filter:
        query = query.filter(DecisionRequest.status == status_filter)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (DecisionRequest.request_id.like(s)) |
            (DecisionRequest.applicant_id.like(s)) |
            (DecisionRequest.request_type.like(s)) |
            (DecisionRequest.description.like(s))
        )
        
    requests = query.order_by(DecisionRequest.submitted_date.desc()).all()
    
    result = []
    for r in requests:
        resps = db.query(ModelResponse).filter(ModelResponse.request_id == r.request_id).all()
        fin = db.query(FinalDecision).filter(FinalDecision.request_id == r.request_id).first()
        
        result.append({
            "id": r.id,
            "request_id": r.request_id,
            "request_type": r.request_type,
            "applicant_id": r.applicant_id,
            "description": r.description,
            "priority": r.priority,
            "risk_level": r.risk_level,
            "submitted_date": r.submitted_date,
            "status": r.status,
            "final_decision": r.final_decision,
            "winning_model": fin.winning_model_name if fin else None,
            "arbitration_score": fin.arbitration_score if fin else None,
            "confidence": fin.confidence if fin else None,
            "policy_used": fin.policy_used if fin else None,
            "model_count": len(resps)
        })
    return result

@router.get("/api/decisions/{request_id}")
def get_decision_detail(request_id: str, db: Session = Depends(get_db)):
    req = db.query(DecisionRequest).filter(DecisionRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Decision request not found.")
    
    responses = db.query(ModelResponse).filter(ModelResponse.request_id == req.request_id).all()
    final_dec = db.query(FinalDecision).filter(FinalDecision.request_id == req.request_id).first()
    audit = db.query(AuditLog).filter(AuditLog.request_id == req.request_id).first()
    
    models = {m.model_id: m for m in db.query(AIModel).all()}
    
    resp_details = []
    for resp in responses:
        m = models.get(resp.model_id)
        resp_details.append({
            "response_id": resp.response_id,
            "model_id": resp.model_id,
            "model_name": m.model_name if m else resp.model_id,
            "vendor_name": m.vendor.vendor_name if (m and m.vendor) else "Vendor",
            "decision": resp.decision,
            "confidence": resp.confidence,
            "reasoning_summary": resp.reasoning_summary,
            "processing_time": resp.processing_time,
            "timestamp": resp.timestamp
        })

    return {
        "request": {
            "id": req.id,
            "request_id": req.request_id,
            "request_type": req.request_type,
            "applicant_id": req.applicant_id,
            "description": req.description,
            "priority": req.priority,
            "risk_level": req.risk_level,
            "submitted_date": req.submitted_date,
            "status": req.status,
            "final_decision": req.final_decision
        },
        "responses": resp_details,
        "final_decision": {
            "final_decision": final_dec.final_decision if final_dec else req.final_decision,
            "winning_model": final_dec.winning_model_name if final_dec else None,
            "arbitration_score": final_dec.arbitration_score if final_dec else None,
            "confidence": final_dec.confidence if final_dec else None,
            "risk_level": final_dec.risk_level if final_dec else req.risk_level,
            "policy_used": final_dec.policy_used if final_dec else None,
            "models_considered": final_dec.models_considered if final_dec else len(responses),
            "agreement_level": final_dec.agreement_level if final_dec else None,
            "explanation": final_dec.explanation if final_dec else None,
            "human_review_required": final_dec.human_review_required if final_dec else False,
            "timestamp": final_dec.timestamp if final_dec else req.submitted_date
        } if final_dec else None,
        "audit": {
            "audit_id": audit.audit_id,
            "timestamp": audit.timestamp,
            "policy_used": audit.policy_used,
            "reviewer": audit.reviewer,
            "reason": audit.reason
        } if audit else None
    }

@router.post("/api/decisions", status_code=status.HTTP_201_CREATED)
def create_and_run_decision(payload: DecisionRequestCreate, db: Session = Depends(get_db)):
    # Create request_id
    req_count = db.query(DecisionRequest).count() + 101
    request_id = f"DR{req_count}"
    
    # 1. Create Decision Request entity
    req = DecisionRequest(
        request_id=request_id,
        request_type=payload.request_type,
        applicant_id=payload.applicant_id,
        description=payload.description,
        priority=payload.priority,
        risk_level=payload.risk_level.upper(),
        submitted_date=datetime.utcnow(),
        status="In Progress",
        final_decision="PENDING"
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    # 2. Get active active models
    active_models = db.query(AIModel).filter(AIModel.status == "Active").all()
    if not active_models:
        raise HTTPException(status_code=400, detail="No active AI models available for arbitration.")
    
    model_ids = [m.model_id for m in active_models]
    if payload.selected_models:
        model_ids = [m for m in payload.selected_models if m in model_ids]

    # 3. Simulate Model Responses
    simulated_outputs = generate_model_responses(request_id=request_id, selected_model_ids=model_ids)
    
    saved_responses = []
    for item in simulated_outputs:
        resp = ModelResponse(
            response_id=item["response_id"],
            request_id=request_id,
            model_id=item["model_id"],
            decision=item["decision"],
            confidence=item["confidence"],
            reasoning_summary=item["reasoning_summary"],
            processing_time=item["processing_time"],
            timestamp=datetime.utcnow()
        )
        db.add(resp)
        saved_responses.append(resp)
    
    db.commit()

    # 4. Fetch Active Policy
    policy = db.query(ArbitrationPolicy).filter(ArbitrationPolicy.is_active == True).first()
    if not policy:
        policy = db.query(ArbitrationPolicy).first() # Fallback to first policy

    # 5. Run Arbitration Engine
    models_dict = {m.model_id: m for m in db.query(AIModel).all()}
    arbitration_res = evaluate_arbitration(req, saved_responses, models_dict, policy)

    # 6. Save Final Decision
    final_dec = FinalDecision(
        request_id=request_id,
        final_decision=arbitration_res["final_decision"],
        winning_model_id=arbitration_res["winning_model_id"],
        winning_model_name=arbitration_res["winning_model"],
        arbitration_score=arbitration_res["arbitration_score"],
        confidence=arbitration_res["confidence"],
        risk_level=arbitration_res["risk_level"],
        policy_used=arbitration_res["policy_used"],
        models_considered=arbitration_res["models_considered"],
        agreement_level=arbitration_res["agreement_level"],
        explanation=arbitration_res["explanation"],
        human_review_required=arbitration_res["human_review_required"],
        timestamp=datetime.utcnow()
    )
    db.add(final_dec)

    # 7. Update Request Status & Final Decision
    if arbitration_res["human_review_required"]:
        req.status = "Pending Human Review"
        req.final_decision = "PENDING HUMAN REVIEW"
        
        # Create Human Review queue item
        h_review = HumanReview(
            review_id=f"HR-{request_id}",
            request_id=request_id,
            risk_level=req.risk_level,
            model_decisions=json.dumps([
                {"model": models_dict.get(r.model_id).model_name, "decision": r.decision, "confidence": r.confidence}
                for r in saved_responses
            ]),
            status="PENDING",
            timestamp=datetime.utcnow()
        )
        db.add(h_review)
    else:
        req.status = "Completed"
        req.final_decision = arbitration_res["final_decision"]

    # 8. Create Audit Log
    audit_count = db.query(AuditLog).count() + 1
    audit = AuditLog(
        audit_id=f"AUD-{audit_count:04d}",
        request_id=request_id,
        timestamp=datetime.utcnow(),
        models_used=",".join([r.model_id for r in saved_responses]),
        model_outputs=json.dumps([
            {"model_id": r.model_id, "decision": r.decision, "confidence": r.confidence, "reason": r.reasoning_summary}
            for r in saved_responses
        ]),
        policy_used=policy.policy_name,
        scores=json.dumps(arbitration_res["scores_breakdown"]),
        final_decision=arbitration_res["final_decision"],
        winning_model=arbitration_res["winning_model"],
        human_review=arbitration_res["human_review_required"],
        reviewer="ArbitrationEngine" if not arbitration_res["human_review_required"] else None,
        reason=arbitration_res["explanation"]
    )
    db.add(audit)
    db.commit()

    return {
        "request_id": request_id,
        "request_type": req.request_type,
        "applicant_id": req.applicant_id,
        "description": req.description,
        "priority": req.priority,
        "risk_level": req.risk_level,
        "status": req.status,
        "model_responses": [
            {
                "response_id": r.response_id,
                "model_id": r.model_id,
                "model_name": models_dict.get(r.model_id).model_name if models_dict.get(r.model_id) else r.model_id,
                "decision": r.decision,
                "confidence": r.confidence,
                "reasoning_summary": r.reasoning_summary,
                "processing_time": r.processing_time
            } for r in saved_responses
        ],
        "arbitration_result": arbitration_res
    }

@router.post("/api/arbitration/run")
def run_arbitration_existing(payload: RunArbitrationPayload, db: Session = Depends(get_db)):
    req = db.query(DecisionRequest).filter(DecisionRequest.request_id == payload.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found.")
    
    responses = db.query(ModelResponse).filter(ModelResponse.request_id == req.request_id).all()
    models_dict = {m.model_id: m for m in db.query(AIModel).all()}

    if payload.policy_id:
        policy = db.query(ArbitrationPolicy).filter(ArbitrationPolicy.policy_id == payload.policy_id).first()
    else:
        policy = db.query(ArbitrationPolicy).filter(ArbitrationPolicy.is_active == True).first()
        
    if not policy:
        policy = db.query(ArbitrationPolicy).first()

    res = evaluate_arbitration(req, responses, models_dict, policy)
    return res
