import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DecisionRequest, ModelResponse, AIModel, ArbitrationPolicy, FinalDecision, AuditLog, HumanReview
from app.simulator import PRESET_SCENARIOS, generate_model_responses
from app.arbitration_engine import evaluate_arbitration

router = APIRouter(prefix="/api/scenarios", tags=["Demo Scenarios"])

@router.get("")
def list_preset_scenarios():
    return [
        {"key": k, "name": v["name"], "description": v["description"], "risk_level": v["risk_level"]}
        for k, v in PRESET_SCENARIOS.items()
    ]

@router.post("/run/{scenario_key}")
def execute_preset_scenario(scenario_key: str, db: Session = Depends(get_db)):
    if scenario_key not in PRESET_SCENARIOS:
        raise HTTPException(status_code=400, detail="Invalid scenario key.")
    
    preset = PRESET_SCENARIOS[scenario_key]
    
    # Generate new request ID
    count = db.query(DecisionRequest).count() + 101
    request_id = f"DR{count}"

    scenario_type_names = {
        "SCENARIO_1": "Permit Approval - Solar Installation",
        "SCENARIO_2": "Infrastructure Funding - Municipal Park",
        "SCENARIO_3": "Construction Permit - Residential High-Rise",
        "SCENARIO_4": "Benefits Eligibility - Low-Income Housing Assistance",
        "SCENARIO_5": "Environmental Approval - Industrial Waste Treatment",
        "SCENARIO_6": "Business License Renewal - Commercial Retail",
        "SCENARIO_7": "Zoning Exception - Mixed-Use Commercial Development",
        "SCENARIO_8": "Hazardous Materials Transport License"
    }

    req_type = scenario_type_names.get(scenario_key, "Public Agency Decision Request")
    
    req = DecisionRequest(
        request_id=request_id,
        request_type=req_type,
        applicant_id=f"APP-{count+500}",
        description=f"[DEMO SCENARIO: {preset['name']}] {preset['description']}",
        priority="High" if preset["risk_level"] in ["HIGH", "CRITICAL"] else "Medium",
        risk_level=preset["risk_level"],
        submitted_date=datetime.utcnow(),
        status="In Progress",
        final_decision="PENDING"
    )
    db.add(req)
    db.commit()

    # Generate scenario responses
    scenario_resps = generate_model_responses(request_id=request_id, scenario_key=scenario_key)
    saved_responses = []
    for item in scenario_resps:
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

    # Evaluate using Active Policy
    policy = db.query(ArbitrationPolicy).filter(ArbitrationPolicy.is_active == True).first()
    if not policy:
        policy = db.query(ArbitrationPolicy).first()

    models_dict = {m.model_id: m for m in db.query(AIModel).all()}
    arbitration_res = evaluate_arbitration(req, saved_responses, models_dict, policy)

    # Save Final Decision
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

    if arbitration_res["human_review_required"]:
        req.status = "Pending Human Review"
        req.final_decision = "PENDING HUMAN REVIEW"

        h_review = HumanReview(
            review_id=f"HR-{request_id}",
            request_id=request_id,
            risk_level=req.risk_level,
            model_decisions=json.dumps([
                {"model": models_dict.get(r.model_id).model_name if models_dict.get(r.model_id) else r.model_id, "decision": r.decision, "confidence": r.confidence}
                for r in saved_responses
            ]),
            status="PENDING",
            timestamp=datetime.utcnow()
        )
        db.add(h_review)
    else:
        req.status = "Completed"
        req.final_decision = arbitration_res["final_decision"]

    # Audit log
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
        "scenario": preset["name"],
        "request_id": request_id,
        "arbitration_result": arbitration_res
    }
