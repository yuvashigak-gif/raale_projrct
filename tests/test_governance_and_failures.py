import pytest
from app.models import DecisionRequest, ModelResponse, AIModel, ArbitrationPolicy
from app.arbitration_engine import evaluate_arbitration

def test_model_failure_fewer_than_two_responses():
    """Verifies that when fewer than 2 models respond, arbitration escalates to human review."""
    req = DecisionRequest(request_id="REQ-FAIL-1", request_type="Permit", applicant_id="APP-F", description="Test", risk_level="LOW")
    pol = ArbitrationPolicy(policy_id="POL-004", policy_name="Standard Policy", is_active=True)

    m1 = AIModel(model_id="M1", model_name="M1", reliability_score=0.9, accuracy_score=0.9, cost_per_request=0.01)
    models_dict = {"M1": m1}

    # Only 1 response returned due to API failure/timeout of other models
    single_response = [ModelResponse(response_id="R1", request_id="REQ-FAIL-1", model_id="M1", decision="APPROVE", confidence=95.0)]

    res = evaluate_arbitration(req, single_response, models_dict, pol)

    assert res["human_review_required"] is True
    assert res["final_decision"] == "PENDING HUMAN REVIEW"
    assert res["selection_method"] == "Insufficient Model Responses"
    assert res["policy_override"] is True
    assert res["winning_model"] is None
    assert "Fewer than 2 active AI models" in res["override_reason"]

def test_critical_risk_disagreement_escalation():
    """Verifies CRITICAL risk level with non-unanimous model votes forces mandatory human review."""
    req = DecisionRequest(request_id="REQ-CRIT", request_type="Hazmat Permit", applicant_id="APP-CRIT", description="Test", risk_level="CRITICAL")
    pol = ArbitrationPolicy(policy_id="POL-004", policy_name="Standard Policy", is_active=True)

    m1 = AIModel(model_id="M1", model_name="M1", reliability_score=0.95, accuracy_score=0.95, cost_per_request=0.01)
    m2 = AIModel(model_id="M2", model_name="M2", reliability_score=0.90, accuracy_score=0.90, cost_per_request=0.01)
    models_dict = {"M1": m1, "M2": m2}

    # Split decision on CRITICAL risk request: M1 APPROVE, M2 REJECT
    r1 = ModelResponse(response_id="R1", request_id="REQ-CRIT", model_id="M1", decision="APPROVE", confidence=92.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-CRIT", model_id="M2", decision="REJECT", confidence=88.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)

    assert res["human_review_required"] is True
    assert res["final_decision"] == "PENDING HUMAN REVIEW"
    assert "Critical Risk Escalated" in res["selection_method"]

def test_high_risk_lack_of_consensus_escalation():
    """Verifies HIGH risk level with no 2 agreeing models forces human review."""
    req = DecisionRequest(request_id="REQ-HIGH", request_type="Demolition", applicant_id="APP-HIGH", description="Test", risk_level="HIGH")
    pol = ArbitrationPolicy(policy_id="POL-004", policy_name="Standard Policy", is_active=True)

    m1 = AIModel(model_id="M1", model_name="M1", reliability_score=0.9, accuracy_score=0.9, cost_per_request=0.01)
    m2 = AIModel(model_id="M2", model_name="M2", reliability_score=0.9, accuracy_score=0.9, cost_per_request=0.01)
    models_dict = {"M1": m1, "M2": m2}

    # Split decision: APPROVE vs REJECT (max_agree_count = 1 < 2)
    r1 = ModelResponse(response_id="R1", request_id="REQ-HIGH", model_id="M1", decision="APPROVE", confidence=90.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-HIGH", model_id="M2", decision="REJECT", confidence=90.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)

    assert res["human_review_required"] is True
    assert res["final_decision"] == "PENDING HUMAN REVIEW"
    assert "High Risk Escalated" in res["selection_method"]

def test_medium_risk_low_confidence_escalation():
    """Verifies MEDIUM risk level with top confidence < 80% forces human review."""
    req = DecisionRequest(request_id="REQ-MED", request_type="Grant", applicant_id="APP-MED", description="Test", risk_level="MEDIUM")
    pol = ArbitrationPolicy(policy_id="POL-004", policy_name="Standard Policy", is_active=True)

    m1 = AIModel(model_id="M1", model_name="M1", reliability_score=0.9, accuracy_score=0.9, cost_per_request=0.01)
    m2 = AIModel(model_id="M2", model_name="M2", reliability_score=0.9, accuracy_score=0.9, cost_per_request=0.01)
    models_dict = {"M1": m1, "M2": m2}

    # Both APPROVE, but confidence is 75% (< 80%)
    r1 = ModelResponse(response_id="R1", request_id="REQ-MED", model_id="M1", decision="APPROVE", confidence=75.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-MED", model_id="M2", decision="APPROVE", confidence=72.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)

    assert res["human_review_required"] is True
    assert res["final_decision"] == "PENDING HUMAN REVIEW"
    assert "Medium Risk Low-Confidence Escalated" in res["selection_method"]
