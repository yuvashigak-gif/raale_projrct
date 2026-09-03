from typing import List, Dict, Any, Tuple
from app.models import ModelResponse, AIModel, ArbitrationPolicy, DecisionRequest

def calculate_consensus_scores(responses: List[ModelResponse]) -> Dict[str, float]:
    """
    Calculates consensus ratio for each response based on how many models share the same decision.
    """
    total = len(responses)
    if total == 0:
        return {}
    
    decision_counts: Dict[str, int] = {}
    for r in responses:
        decision_counts[r.decision] = decision_counts.get(r.decision, 0) + 1
        
    consensus_scores: Dict[str, float] = {}
    for r in responses:
        count = decision_counts[r.decision]
        consensus_scores[r.response_id] = count / total
        
    return consensus_scores

def evaluate_arbitration(
    request: DecisionRequest,
    responses: List[ModelResponse],
    models_dict: Dict[str, AIModel],
    policy: ArbitrationPolicy
) -> Dict[str, Any]:
    """
    Core Arbitration Algorithm evaluating model responses under selected policy and request risk level.
    Returns structured final decision analysis object.
    """
    if not responses or len(responses) < 2:
        return {
            "request_id": request.request_id,
            "final_decision": "PENDING HUMAN REVIEW",
            "winning_model": None,
            "winning_model_id": None,
            "arbitration_score": 0.0,
            "confidence": 0.0,
            "risk_level": request.risk_level,
            "policy_used": policy.policy_name,
            "models_considered": len(responses),
            "agreement_level": "0 of 0",
            "explanation": "Arbitration could not be completed because fewer than two active models returned valid responses.",
            "human_review_required": True,
            "scores_breakdown": []
        }

    total_models = len(responses)
    consensus_map = calculate_consensus_scores(responses)

    # Group responses by decision type (APPROVE, REJECT, REVIEW)
    decisions_group: Dict[str, List[ModelResponse]] = {}
    for r in responses:
        decisions_group.setdefault(r.decision, []).append(r)

    # Count agreement
    decision_counts = {dec: len(m_list) for dec, m_list in decisions_group.items()}
    max_agree_count = max(decision_counts.values()) if decision_counts else 0
    majority_decision = max(decision_counts, key=decision_counts.get) if decision_counts else "REVIEW"
    agreement_level = f"{max_agree_count} of {total_models} models"

    # Calculate model individual weighted scores
    w_rel = policy.weight_reliability
    w_conf = policy.weight_confidence
    w_acc = policy.weight_accuracy
    w_cons = policy.weight_consensus

    scores_breakdown = []
    response_scores = {}

    for r in responses:
        model = models_dict.get(r.model_id)
        rel = model.reliability_score if model else 0.90
        acc = model.accuracy_score if model else 0.90
        conf = r.confidence / 100.0 if r.confidence > 1.0 else r.confidence
        cons = consensus_map.get(r.response_id, 0.5)

        # Weighted Score Formula (0-100 scale)
        weighted_score = (rel * w_rel + conf * w_conf + acc * w_acc + cons * w_cons) * 100.0
        response_scores[r.response_id] = weighted_score

        scores_breakdown.append({
            "response_id": r.response_id,
            "model_id": r.model_id,
            "model_name": model.model_name if model else r.model_id,
            "decision": r.decision,
            "confidence": round(conf * 100, 1),
            "reliability": round(rel * 100, 1),
            "accuracy": round(acc * 100, 1),
            "consensus": round(cons * 100, 1),
            "arbitration_score": round(weighted_score, 2)
        })

    # Pick response with highest arbitration score
    top_response = max(responses, key=lambda r: response_scores[r.response_id])
    top_score = response_scores[top_response.response_id]
    top_model = models_dict.get(top_response.model_id)
    top_model_name = top_model.model_name if top_model else top_response.model_id
    top_confidence = top_response.confidence if top_response.confidence > 1.0 else top_response.confidence * 100.0

    # Policy & Risk Evaluation Logic
    policy_id = policy.policy_id
    human_review_required = False
    final_decision_str = top_response.decision
    explanation = ""

    # Rule checks based on policy:
    if policy_id == "POL-001": # Majority Voting
        final_decision_str = majority_decision
        explanation = f"Majority Voting policy selected '{majority_decision}' as {agreement_level} agreed."
    
    elif policy_id == "POL-002": # Weighted Confidence
        # Sum confidence per decision
        conf_sums = {}
        for r in responses:
            c = r.confidence if r.confidence > 1.0 else r.confidence * 100.0
            conf_sums[r.decision] = conf_sums.get(r.decision, 0) + c
        best_conf_dec = max(conf_sums, key=conf_sums.get)
        final_decision_str = best_conf_dec
        explanation = f"Weighted Confidence policy selected '{best_conf_dec}' based on cumulative model confidence."

    elif policy_id == "POL-003": # Highest Reliability
        # Model with highest reliability wins
        rel_sorted = sorted(responses, key=lambda r: models_dict.get(r.model_id, AIModel()).reliability_score, reverse=True)
        winning_rel_r = rel_sorted[0]
        final_decision_str = winning_rel_r.decision
        winning_model = models_dict.get(winning_rel_r.model_id)
        explanation = f"Highest Reliability policy selected decision '{final_decision_str}' from top-rated model ({winning_model.model_name if winning_model else winning_rel_r.model_id})."

    elif policy_id == "POL-005": # Human Review on Disagreement
        if len(decisions_group) > 1:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            explanation = f"Models disagreed ({agreement_level}). Policy POL-005 strictly mandates human review on disagreement."

    elif policy_id == "POL-006": # High Risk -> Human Review
        if request.risk_level in ["HIGH", "CRITICAL"]:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            explanation = f"Request risk level is {request.risk_level}. Policy POL-006 mandates human review for high-risk requests."

    elif policy_id == "POL-007": # Minimum Confidence Threshold
        threshold = policy.min_confidence_threshold * 100.0
        if top_confidence < threshold:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            explanation = f"Top model confidence ({round(top_confidence, 1)}%) is below the minimum policy threshold ({round(threshold, 1)}%). Sent to human review."

    elif policy_id == "POL-008": # Consensus Required
        consensus_pct = max_agree_count / total_models
        if consensus_pct < 0.75:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            explanation = f"Model consensus ({round(consensus_pct*100, 1)}%) did not meet the required threshold. Escalate to human review."

    elif policy_id == "POL-009": # Two-Model Agreement
        if max_agree_count < 2:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            explanation = "No two models agreed on a decision. Human review required under POL-009."

    # General Risk Level Enforcement (Applies to POL-004, POL-010, and all general policies)
    if not human_review_required:
        if request.risk_level == "CRITICAL" and len(decisions_group) > 1:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            explanation = f"Critical risk request with conflicting model opinions ({agreement_level}). Escalated to mandatory human review."

        elif request.risk_level == "HIGH" and max_agree_count < 2:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            explanation = f"High risk request failed to reach strong consensus ({agreement_level}). Escalated to human review."

        elif request.risk_level == "MEDIUM" and top_confidence < 80.0:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            explanation = f"Medium risk request top confidence ({round(top_confidence, 1)}%) fell below automatic threshold (80.0%). Sent to human review."

        elif not explanation:
            explanation = f"{agreement_level} recommended {final_decision_str}. Top winning model '{top_model_name}' achieved highest weighted arbitration score ({round(top_score, 1)}/100) under policy '{policy.policy_name}'."

    return {
        "request_id": request.request_id,
        "final_decision": final_decision_str,
        "winning_model": top_model_name if not human_review_required else None,
        "winning_model_id": top_response.model_id if not human_review_required else None,
        "arbitration_score": round(top_score, 2),
        "confidence": round(top_confidence, 1),
        "risk_level": request.risk_level,
        "policy_used": policy.policy_name,
        "models_considered": total_models,
        "agreement_level": agreement_level,
        "explanation": explanation,
        "human_review_required": human_review_required,
        "scores_breakdown": scores_breakdown
    }
