import pytest
import json
from app.models import AuditLog, DecisionRequest, FinalDecision, HumanReview, ArbitrationPolicy

def test_audit_log_creation_and_api(db_session, client):
    """Verifies creation of audit logs and GET /api/audit-logs endpoint."""
    req = DecisionRequest(request_id="DR-AUDIT-1", request_type="Permit", applicant_id="APP-A", description="Test audit", risk_level="LOW")
    db_session.add(req)
    db_session.commit()

    audit = AuditLog(
        audit_id="AUD-0001",
        request_id="DR-AUDIT-1",
        models_used="M1,M2",
        model_outputs=json.dumps([{"model_id": "M1", "decision": "APPROVE", "confidence": 90}]),
        policy_used="Weighted Reliability + Confidence",
        scores=json.dumps([{"model_id": "M1", "arbitration_score": 92.5}]),
        final_decision="APPROVE",
        winning_model="GPT-Heavy",
        weighted_score_winner="GPT-Heavy",
        policy_selected_winner="GPT-Heavy",
        selection_method="Weighted Scoring",
        policy_override=False,
        override_reason="None - Weighted score winner aligns with policy decision.",
        risk_level="LOW",
        human_review=False,
        reviewer="ArbitrationEngine",
        reason="Automated consensus approval"
    )
    db_session.add(audit)
    db_session.commit()

    res = client.get("/api/audit-logs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 1
    first = logs[0]
    assert first["audit_id"] == "AUD-0001"
    assert first["request_id"] == "DR-AUDIT-1"
    assert first["final_decision"] == "APPROVE"
    assert first["weighted_score_winner"] == "GPT-Heavy"
    assert first["policy_selected_winner"] == "GPT-Heavy"
    assert first["policy_override"] is False

def test_create_decision_endpoint(client, sample_models, sample_policy):
    """Verifies POST /api/decisions endpoint submits request and runs arbitration."""
    payload = {
        "request_type": "Permit Approval",
        "applicant_id": "APP-POST-1",
        "description": "Commercial building permit application",
        "priority": "High",
        "risk_level": "LOW",
        "model_responses": [
            {"model_id": "M_HIGH_COST", "decision": "APPROVE", "confidence": 92.0, "reasoning_summary": "Meets specs"},
            {"model_id": "M_LOW_COST", "decision": "APPROVE", "confidence": 88.0, "reasoning_summary": "Clearance valid"}
        ]
    }

    res = client.post("/api/decisions", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "request_id" in data
    assert "arbitration_result" in data
    arb = data["arbitration_result"]
    assert arb["final_decision"] == "APPROVE"
    assert arb["weighted_score_winner"] is not None
    assert arb["policy_selected_winner"] is not None

def test_get_vendors_and_models_api(client, sample_vendor, sample_models):
    """Verifies GET /api/vendors and GET /api/models endpoints."""
    res_v = client.get("/api/vendors")
    assert res_v.status_code == 200
    vendors = res_v.json()
    assert len(vendors) >= 1

    res_m = client.get("/api/models")
    assert res_m.status_code == 200
    models = res_m.json()
    assert len(models) >= 3

def test_get_and_activate_policies_api(client, sample_policy):
    """Verifies GET /api/policies and PUT /api/policies/{id}/activate endpoints."""
    res_p = client.get("/api/policies")
    assert res_p.status_code == 200
    policies = res_p.json()
    assert len(policies) >= 1

    pol_id = sample_policy.policy_id
    res_act = client.put(f"/api/policies/{pol_id}/activate")
    assert res_act.status_code == 200

def test_human_review_and_scenarios_api(client, db_session):
    """Verifies human review processing and preset demo scenarios execution endpoints."""
    # Seed a pending human review
    hr = HumanReview(
        review_id="HR-TEST-1",
        request_id="DR-HR-1",
        risk_level="HIGH",
        model_decisions=json.dumps([{"model": "GPT-5.6", "decision": "APPROVE", "confidence": 90}]),
        status="PENDING"
    )
    req = DecisionRequest(request_id="DR-HR-1", request_type="Permit", applicant_id="APP-1", description="Test", risk_level="HIGH", status="Pending Human Review", final_decision="PENDING HUMAN REVIEW")
    db_session.add_all([hr, req])
    db_session.commit()

    # Get human reviews
    res_hr = client.get("/api/human-review")
    assert res_hr.status_code == 200
    assert len(res_hr.json()) >= 1

    # Process human review
    review_payload = {
        "review_id": "HR-TEST-1",
        "human_decision": "APPROVE",
        "reviewer_name": "Senior Auditor Jane",
        "review_notes": "Manually verified compliance documents."
    }
    res_proc = client.post("/api/human-review", json=review_payload)
    assert res_proc.status_code == 200
    assert res_proc.json()["status"] == "APPROVED"

    # Test preset demo scenarios
    res_sc = client.get("/api/scenarios")
    assert res_sc.status_code == 200
    scenarios = res_sc.json()
    assert len(scenarios) == 8

    # Execute scenario 1
    sc1_key = scenarios[0]["key"]
    res_run = client.post(f"/api/scenarios/run/{sc1_key}")
    assert res_run.status_code == 200
    assert "arbitration_result" in res_run.json()
