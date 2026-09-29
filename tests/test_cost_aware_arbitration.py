import pytest
from app.models import DecisionRequest, ModelResponse, AIModel, ArbitrationPolicy
from app.arbitration_engine import evaluate_arbitration

def test_model_cost_per_request_extraction():
    """Verifies that cost_per_request is correctly extracted and reflected in breakdown."""
    req = DecisionRequest(request_id="REQ-COST-1", request_type="Permit Approval", applicant_id="APP-1", description="Test", risk_level="LOW")
    
    m1 = AIModel(model_id="M1", model_name="Expensive-Model", reliability_score=0.95, accuracy_score=0.95, cost_per_request=0.050)
    m2 = AIModel(model_id="M2", model_name="Cheap-Model", reliability_score=0.90, accuracy_score=0.90, cost_per_request=0.005)
    models_dict = {"M1": m1, "M2": m2}

    pol = ArbitrationPolicy(
        policy_id="POL-004", policy_name="Test Policy", is_active=True,
        weight_reliability=0.2, weight_confidence=0.2, weight_accuracy=0.2, weight_consensus=0.2, weight_cost=0.2
    )

    r1 = ModelResponse(response_id="R1", request_id="REQ-COST-1", model_id="M1", decision="APPROVE", confidence=90.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-COST-1", model_id="M2", decision="APPROVE", confidence=90.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)

    assert res["total_cost"] == 0.055
    breakdown_map = {b["model_id"]: b for b in res["scores_breakdown"]}
    assert breakdown_map["M1"]["cost_per_request"] == 0.050
    assert breakdown_map["M2"]["cost_per_request"] == 0.005
    # Cheap model should get higher cost score (100.0) compared to expensive model (0.0)
    assert breakdown_map["M2"]["cost_score"] == 100.0
    assert breakdown_map["M1"]["cost_score"] == 0.0

def test_cost_aware_arbitration_influences_winner():
    """Verifies that high cost weight gives advantage to cheaper model when other metrics are close."""
    req = DecisionRequest(request_id="REQ-COST-2", request_type="Benefits", applicant_id="APP-2", description="Test", risk_level="LOW")

    m1 = AIModel(model_id="M1", model_name="Expensive Model", reliability_score=0.91, accuracy_score=0.91, cost_per_request=0.100)
    m2 = AIModel(model_id="M2", model_name="Economical Model", reliability_score=0.90, accuracy_score=0.90, cost_per_request=0.001)
    models_dict = {"M1": m1, "M2": m2}

    # Policy with high weight on cost (50% weight on cost)
    pol = ArbitrationPolicy(
        policy_id="POL-004", policy_name="Cost Heavy Policy", is_active=True,
        weight_reliability=0.1, weight_confidence=0.2, weight_accuracy=0.1, weight_consensus=0.1, weight_cost=0.5
    )

    r1 = ModelResponse(response_id="R1", request_id="REQ-COST-2", model_id="M1", decision="APPROVE", confidence=88.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-COST-2", model_id="M2", decision="APPROVE", confidence=88.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)

    assert res["weighted_score_winner_id"] == "M2"
    assert res["policy_selected_winner_id"] == "M2"
    assert res["winning_model"] == "Economical Model"

def test_missing_or_invalid_cost_fallback():
    """Verifies that missing, None, or negative model cost defaults gracefully to 0.010 without crashing."""
    req = DecisionRequest(request_id="REQ-INVALID-COST", request_type="License", applicant_id="APP-3", description="Test", risk_level="LOW")

    m1 = AIModel(model_id="M1", model_name="Model None Cost", reliability_score=0.90, accuracy_score=0.90, cost_per_request=None)
    m2 = AIModel(model_id="M2", model_name="Model Neg Cost", reliability_score=0.90, accuracy_score=0.90, cost_per_request=-0.05)
    models_dict = {"M1": m1, "M2": m2}

    pol = ArbitrationPolicy(policy_id="POL-004", policy_name="Default Policy", is_active=True)

    r1 = ModelResponse(response_id="R1", request_id="REQ-INVALID-COST", model_id="M1", decision="APPROVE", confidence=85.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-INVALID-COST", model_id="M2", decision="APPROVE", confidence=85.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)

    assert res["total_cost"] == 0.020  # 0.010 + 0.010 fallback
    for b in res["scores_breakdown"]:
        assert b["cost_per_request"] == 0.010
