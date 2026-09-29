import pytest
from app.models import DecisionRequest, ModelResponse, AIModel, ArbitrationPolicy
from app.arbitration_engine import evaluate_arbitration, calculate_consensus_scores

def test_consensus_score_calculation():
    """Verifies that calculate_consensus_scores calculates correct ratio of agreeing models."""
    resps = [
        ModelResponse(response_id="R1", decision="APPROVE"),
        ModelResponse(response_id="R2", decision="APPROVE"),
        ModelResponse(response_id="R3", decision="REJECT")
    ]
    scores = calculate_consensus_scores(resps)
    assert scores["R1"] == pytest.approx(2/3)
    assert scores["R2"] == pytest.approx(2/3)
    assert scores["R3"] == pytest.approx(1/3)

def test_weighted_scoring_formula():
    """Verifies exact weighted score formula calculation on 0-100 scale."""
    req = DecisionRequest(request_id="REQ-WS", request_type="Zoning", applicant_id="APP-WS", description="Test", risk_level="LOW")
    
    m1 = AIModel(model_id="M1", model_name="M1", reliability_score=0.90, accuracy_score=0.80, cost_per_request=0.010)
    m2 = AIModel(model_id="M2", model_name="M2", reliability_score=0.90, accuracy_score=0.80, cost_per_request=0.010)
    models_dict = {"M1": m1, "M2": m2}

    pol = ArbitrationPolicy(
        policy_id="POL-004", policy_name="Weighted Score Test", is_active=True,
        weight_reliability=0.30, weight_confidence=0.25, weight_accuracy=0.15, weight_consensus=0.15, weight_cost=0.15
    )

    # 100% confidence, consensus = 1.0 (both APPROVE), max_cost = 0.010 -> cost_score = 1.0
    r1 = ModelResponse(response_id="R1", request_id="REQ-WS", model_id="M1", decision="APPROVE", confidence=100.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-WS", model_id="M2", decision="APPROVE", confidence=100.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)
    
    # Expected weighted score: (0.90*0.30 + 1.0*0.25 + 0.80*0.15 + 1.0*0.15 + 1.0*0.15) / 1.0 * 100
    # = (0.27 + 0.25 + 0.12 + 0.15 + 0.15) * 100 = 94.0
    b = res["scores_breakdown"][0]
    assert b["arbitration_score"] == 94.0

def test_policy_majority_voting_pol_001():
    """Verifies POL-001 (Majority Voting) selects decision supported by majority of models."""
    req = DecisionRequest(request_id="REQ-MAJ", request_type="Grant", applicant_id="APP-MAJ", description="Test", risk_level="LOW")
    
    m1 = AIModel(model_id="M1", model_name="Model 1", reliability_score=0.99, accuracy_score=0.99, cost_per_request=0.010)
    m2 = AIModel(model_id="M2", model_name="Model 2", reliability_score=0.85, accuracy_score=0.85, cost_per_request=0.010)
    m3 = AIModel(model_id="M3", model_name="Model 3", reliability_score=0.85, accuracy_score=0.85, cost_per_request=0.010)
    models_dict = {"M1": m1, "M2": m2, "M3": m3}

    pol = ArbitrationPolicy(policy_id="POL-001", policy_name="Majority Voting", is_active=True, consensus_required=True)

    # M1 votes REJECT (highest raw score model), but M2 & M3 vote APPROVE (2 vs 1 majority)
    r1 = ModelResponse(response_id="R1", request_id="REQ-MAJ", model_id="M1", decision="REJECT", confidence=98.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-MAJ", model_id="M2", decision="APPROVE", confidence=85.0)
    r3 = ModelResponse(response_id="R3", request_id="REQ-MAJ", model_id="M3", decision="APPROVE", confidence=85.0)

    res = evaluate_arbitration(req, [r1, r2, r3], models_dict, pol)

    assert res["selection_method"] == "Majority Voting"
    assert res["final_decision"] == "APPROVE"
    assert res["weighted_score_winner_id"] == "M1"
    assert res["policy_selected_winner_id"] in ["M2", "M3"]
    assert res["policy_override"] is True

def test_policy_highest_reliability_pol_003():
    """Verifies POL-003 selects decision of highest reliability model."""
    req = DecisionRequest(request_id="REQ-REL", request_type="Permit", applicant_id="APP-REL", description="Test", risk_level="LOW")

    m1 = AIModel(model_id="M1", model_name="Low Rel Model", reliability_score=0.80, accuracy_score=0.80, cost_per_request=0.010)
    m2 = AIModel(model_id="M2", model_name="High Rel Model", reliability_score=0.98, accuracy_score=0.80, cost_per_request=0.010)
    models_dict = {"M1": m1, "M2": m2}

    pol = ArbitrationPolicy(policy_id="POL-003", policy_name="Highest Reliability", is_active=True)

    # M1 has 99% confidence but lower reliability (0.80) vs M2 reliability (0.98)
    r1 = ModelResponse(response_id="R1", request_id="REQ-REL", model_id="M1", decision="REJECT", confidence=99.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-REL", model_id="M2", decision="APPROVE", confidence=85.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)

    assert res["selection_method"] == "Highest Reliability"
    assert res["policy_selected_winner_id"] == "M2"
    assert res["final_decision"] == "APPROVE"

def test_policy_minimum_confidence_threshold_pol_007():
    """Verifies POL-007 escalates when top confidence is below threshold."""
    req = DecisionRequest(request_id="REQ-THRESH", request_type="License", applicant_id="APP-T", description="Test", risk_level="LOW")

    m1 = AIModel(model_id="M1", model_name="Model 1", reliability_score=0.90, accuracy_score=0.90, cost_per_request=0.010)
    m2 = AIModel(model_id="M2", model_name="Model 2", reliability_score=0.90, accuracy_score=0.90, cost_per_request=0.010)
    models_dict = {"M1": m1, "M2": m2}

    # Policy requires 85% min confidence
    pol = ArbitrationPolicy(policy_id="POL-007", policy_name="Min Confidence Threshold", min_confidence_threshold=0.85, is_active=True)

    # Top confidence is 80.0% (< 85%)
    r1 = ModelResponse(response_id="R1", request_id="REQ-THRESH", model_id="M1", decision="APPROVE", confidence=80.0)
    r2 = ModelResponse(response_id="R2", request_id="REQ-THRESH", model_id="M2", decision="APPROVE", confidence=78.0)

    res = evaluate_arbitration(req, [r1, r2], models_dict, pol)

    assert res["human_review_required"] is True
    assert res["final_decision"] == "PENDING HUMAN REVIEW"
    assert res["policy_override"] is True
