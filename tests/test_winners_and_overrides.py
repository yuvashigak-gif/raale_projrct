import pytest
from app.models import DecisionRequest, ModelResponse, AIModel, ArbitrationPolicy
from app.arbitration_engine import evaluate_arbitration

def test_winner_alignment_no_override():
    """Verifies policy_override is False when weighted score winner matches policy selected winner."""
    req = DecisionRequest(request_id="REQ-ALIGN", request_type="Permit", applicant_id="APP-1", description="Test", risk_level="LOW")

    m1 = AIModel(model_id="M1", model_name="Best Model", reliability_score=0.96, accuracy_score=0.96, cost_per_request=0.010)
    m2 = AIModel(model_id="M2", model_name="Standard Model", reliability_score=0.88, accuracy_score=0.88, cost_per_request=0.010)
    models_dict = {"M1": m1, "M2": m2}

    pol = ArbitrationPolicy(policy_id="POL-004", policy_name="Weighted Policy", is_active=True)

    r1 = ModelResponse(response_id="R1", request_id="REQ-ALIGN", model_id="M1", decision="APPROVE", confidence=95.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-ALIGN", model_id="M2", decision="APPROVE", confidence=85.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)

    assert res["weighted_score_winner"] == "Best Model"
    assert res["policy_selected_winner"] == "Best Model"
    assert res["winning_model"] == "Best Model"
    assert res["final_decision"] == "APPROVE"
    assert res["policy_override"] is False
    assert "None - Weighted score winner" in res["override_reason"]

def test_winner_mismatch_triggers_policy_override():
    """Verifies policy_override is True when policy selected winner differs from weighted score winner."""
    req = DecisionRequest(request_id="REQ-MISMATCH", request_type="Permit", applicant_id="APP-2", description="Test", risk_level="LOW")

    m1 = AIModel(model_id="M1", model_name="Highest Raw Score Model", reliability_score=0.98, accuracy_score=0.98, cost_per_request=0.010)
    m2 = AIModel(model_id="M2", model_name="Majority Consensus Model", reliability_score=0.85, accuracy_score=0.85, cost_per_request=0.010)
    m3 = AIModel(model_id="M3", model_name="Majority Partner Model", reliability_score=0.85, accuracy_score=0.85, cost_per_request=0.010)
    models_dict = {"M1": m1, "M2": m2, "M3": m3}

    # Majority Voting Policy
    pol = ArbitrationPolicy(policy_id="POL-001", policy_name="Majority Voting", is_active=True)

    # M1 votes REJECT (highest raw weighted score), M2 & M3 vote APPROVE
    r1 = ModelResponse(response_id="R1", request_id="REQ-MISMATCH", model_id="M1", decision="REJECT", confidence=99.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-MISMATCH", model_id="M2", decision="APPROVE", confidence=80.0)
    r3 = ModelResponse(response_id="R3", request_id="REQ-MISMATCH", model_id="M3", decision="APPROVE", confidence=80.0)

    res = evaluate_arbitration(req, [r1, r2, r3], models_dict, pol)

    assert res["weighted_score_winner"] == "Highest Raw Score Model"
    assert res["policy_selected_winner"] in ["Majority Consensus Model", "Majority Partner Model"]
    assert res["final_decision"] == "APPROVE"
    assert res["policy_override"] is True
    assert "selected" in res["override_reason"] and "highest raw weighted" in res["override_reason"]

def test_final_decision_outcomes():
    """Verifies that final_decision produces APPROVE, REJECT, or PENDING HUMAN REVIEW appropriately."""
    req_approve = DecisionRequest(request_id="REQ-F1", request_type="P", applicant_id="A", description="d", risk_level="LOW")
    req_reject = DecisionRequest(request_id="REQ-F2", request_type="P", applicant_id="A", description="d", risk_level="LOW")

    m1 = AIModel(model_id="M1", model_name="M1", reliability_score=0.9, accuracy_score=0.9, cost_per_request=0.01)
    m2 = AIModel(model_id="M2", model_name="M2", reliability_score=0.9, accuracy_score=0.9, cost_per_request=0.01)
    models = {"M1": m1, "M2": m2}
    pol = ArbitrationPolicy(policy_id="POL-004", policy_name="Standard", is_active=True)

    # All APPROVE
    r_app = [ModelResponse(response_id="1", model_id="M1", decision="APPROVE", confidence=90), ModelResponse(response_id="2", model_id="M2", decision="APPROVE", confidence=90)]
    res1 = evaluate_arbitration(req_approve, r_app, models, pol)
    assert res1["final_decision"] == "APPROVE"

    # All REJECT
    r_rej = [ModelResponse(response_id="3", model_id="M1", decision="REJECT", confidence=90), ModelResponse(response_id="4", model_id="M2", decision="REJECT", confidence=90)]
    res2 = evaluate_arbitration(req_reject, r_rej, models, pol)
    assert res2["final_decision"] == "REJECT"
