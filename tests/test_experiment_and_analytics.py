import pytest
from app.experiment import run_baseline_vs_arbitration_experiment, SYNTHETIC_VALIDATION_DATASET
from app.models import ArbitrationPolicy, DecisionRequest, FinalDecision, AIModel, ModelResponse, Vendor, HumanReview
from app.routers.analytics import get_analytics

def test_run_baseline_vs_arbitration_experiment():
    """Verifies baseline vs proposed arbitration experiment execution and metric calculations."""
    policy = ArbitrationPolicy(
        policy_id="POL-004", policy_name="Weighted Reliability + Confidence",
        is_active=True, weight_reliability=0.30, weight_confidence=0.25,
        weight_accuracy=0.15, weight_consensus=0.15, weight_cost=0.15
    )

    metrics = run_baseline_vs_arbitration_experiment(policy)

    assert metrics["dataset_name"] == "Synthetic Validation Dataset"
    assert metrics["total_cases_evaluated"] == 50
    assert "baseline_decision_quality" in metrics
    assert "arbitration_decision_quality" in metrics
    assert "conflict_resolution_rate" in metrics
    assert "human_review_rate" in metrics
    assert "policy_override_rate" in metrics
    assert metrics["avg_baseline_cost_per_decision"] > 0
    assert metrics["avg_arbitration_cost_per_decision"] > 0
    assert len(metrics["case_details"]) == 10

def test_analytics_calculations_and_api(db_session, client, sample_vendor, sample_models, sample_policy):
    """Verifies analytics computation logic and GET /api/analytics response."""
    # Seed a decision request and final decision
    req = DecisionRequest(request_id="DR-AN-1", request_type="Permit", applicant_id="APP-1", description="Test", risk_level="LOW", final_decision="APPROVE")
    db_session.add(req)
    db_session.commit()

    fd = FinalDecision(
        request_id="DR-AN-1", final_decision="APPROVE", winning_model_id="M_LOW_COST", winning_model_name="Gemini-Lite",
        weighted_score_winner_id="M_LOW_COST", weighted_score_winner_name="Gemini-Lite",
        policy_selected_winner_id="M_LOW_COST", policy_selected_winner_name="Gemini-Lite",
        selection_method="Weighted Scoring", policy_override=False, total_cost=0.015,
        arbitration_score=92.5, confidence=90.0, risk_level="LOW", policy_used="POL-004",
        models_considered=2, agreement_level="2 of 2 models", explanation="Test explanation", human_review_required=False
    )
    db_session.add(fd)
    db_session.commit()

    # Call get_analytics function directly
    stats = get_analytics(db_session)
    assert stats["total_decisions"] == 1
    assert stats["approved_count"] == 1
    assert stats["rejected_count"] == 0
    assert "average_confidence" in stats
    assert "model_stats" in stats
    assert "experiment_results" in stats

    # Test HTTP API endpoint
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_decisions"] == 1
    assert data["approved_count"] == 1
