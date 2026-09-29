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
    Core Arbitration Algorithm evaluating model responses under selected policy, monetary cost weights,
    and request risk level governance.
    Returns structured final decision analysis object cleanly separating weighted winner from policy winner.
    """
    total_models = len(responses) if responses else 0
    total_cost = 0.0

    if not responses or total_models < 2:
        return {
            "request_id": request.request_id,
            "final_decision": "PENDING HUMAN REVIEW",
            "winning_model": None,
            "winning_model_id": None,
            "weighted_score_winner": None,
            "weighted_score_winner_id": None,
            "policy_selected_winner": None,
            "policy_selected_winner_id": None,
            "selection_method": "Insufficient Model Responses",
            "policy_override": True,
            "override_reason": "Fewer than 2 active AI models responded to request. System mandated escalation to human review queue.",
            "total_cost": 0.0,
            "arbitration_score": 0.0,
            "confidence": 0.0,
            "risk_level": request.risk_level,
            "policy_used": policy.policy_name if policy else "Default Policy",
            "models_considered": total_models,
            "agreement_level": f"{total_models} of {total_models} models",
            "explanation": "Arbitration could not be completed automatically because fewer than two active models returned valid responses. Escalated to human review.",
            "human_review_required": True,
            "scores_breakdown": []
        }

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

    # 1. Cost Calculations & Normalization
    model_costs = []
    for r in responses:
        m = models_dict.get(r.model_id)
        c = getattr(m, "cost_per_request", 0.010) if m else 0.010
        if c is None or c < 0:
            c = 0.010
        model_costs.append(c)
        total_cost += c

    max_cost = max(model_costs) if model_costs else 0.010
    total_cost = round(total_cost, 4)

    # Policy weight components
    w_rel = getattr(policy, "weight_reliability", 0.30)
    w_conf = getattr(policy, "weight_confidence", 0.25)
    w_acc = getattr(policy, "weight_accuracy", 0.15)
    w_cons = getattr(policy, "weight_consensus", 0.15)
    w_cost = getattr(policy, "weight_cost", 0.15)

    sum_weights = w_rel + w_conf + w_acc + w_cons + w_cost
    if sum_weights <= 0:
        sum_weights = 1.0

    scores_breakdown = []
    response_scores = {}

    for i, r in enumerate(responses):
        model = models_dict.get(r.model_id)
        rel = model.reliability_score if model else 0.90
        acc = model.accuracy_score if model else 0.90
        conf = r.confidence / 100.0 if r.confidence > 1.0 else r.confidence
        cons = consensus_map.get(r.response_id, 0.5)
        cost = model_costs[i]

        # Normalized cost score (0.0 to 1.0) - Lower cost yields higher cost_score
        cost_score = 1.0 if max_cost <= 0 else max(0.0, 1.0 - (cost / max_cost))

        # Weighted Score Formula (0-100 scale)
        weighted_score = ((rel * w_rel + conf * w_conf + acc * w_acc + cons * w_cons + cost_score * w_cost) / sum_weights) * 100.0
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
            "cost_per_request": round(cost, 4),
            "cost_score": round(cost_score * 100, 1),
            "arbitration_score": round(weighted_score, 2)
        })

    # Pick response with highest weighted arbitration score
    top_weighted_response = max(responses, key=lambda r: response_scores[r.response_id])
    top_weighted_score = response_scores[top_weighted_response.response_id]
    top_weighted_model = models_dict.get(top_weighted_response.model_id)
    weighted_score_winner_name = top_weighted_model.model_name if top_weighted_model else top_weighted_response.model_id
    weighted_score_winner_id = top_weighted_response.model_id
    top_confidence = top_weighted_response.confidence if top_weighted_response.confidence > 1.0 else top_weighted_response.confidence * 100.0

    # 2. Policy-Specific Decision & Selection Method
    policy_id = policy.policy_id if policy else "POL-004"
    policy_selected_winner_id = weighted_score_winner_id
    policy_selected_winner_name = weighted_score_winner_name
    final_decision_str = top_weighted_response.decision
    selection_method = "Weighted Scoring"
    human_review_required = False

    if policy_id == "POL-001": # Majority Voting
        selection_method = "Majority Voting"
        final_decision_str = majority_decision
        # Pick model supporting majority decision with highest weighted score
        maj_responses = decisions_group.get(majority_decision, [])
        if maj_responses:
            top_maj = max(maj_responses, key=lambda r: response_scores[r.response_id])
            policy_selected_winner_id = top_maj.model_id
            m_obj = models_dict.get(top_maj.model_id)
            policy_selected_winner_name = m_obj.model_name if m_obj else top_maj.model_id

    elif policy_id == "POL-002": # Weighted Confidence
        selection_method = "Weighted Confidence"
        conf_sums = {}
        for r in responses:
            c = r.confidence if r.confidence > 1.0 else r.confidence * 100.0
            conf_sums[r.decision] = conf_sums.get(r.decision, 0) + c
        best_conf_dec = max(conf_sums, key=conf_sums.get)
        final_decision_str = best_conf_dec
        # Pick top confidence model for that decision
        matching_resps = decisions_group.get(best_conf_dec, [])
        if matching_resps:
            top_c_resp = max(matching_resps, key=lambda r: r.confidence if r.confidence > 1.0 else r.confidence * 100.0)
            policy_selected_winner_id = top_c_resp.model_id
            m_obj = models_dict.get(top_c_resp.model_id)
            policy_selected_winner_name = m_obj.model_name if m_obj else top_c_resp.model_id

    elif policy_id == "POL-003": # Highest Reliability
        selection_method = "Highest Reliability"
        rel_sorted = sorted(responses, key=lambda r: models_dict.get(r.model_id, AIModel()).reliability_score, reverse=True)
        winning_rel_r = rel_sorted[0]
        final_decision_str = winning_rel_r.decision
        policy_selected_winner_id = winning_rel_r.model_id
        m_obj = models_dict.get(winning_rel_r.model_id)
        policy_selected_winner_name = m_obj.model_name if m_obj else winning_rel_r.model_id

    elif policy_id == "POL-005": # Human Review on Disagreement
        selection_method = "Disagreement Escalation"
        if len(decisions_group) > 1:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            policy_selected_winner_id = None
            policy_selected_winner_name = None

    elif policy_id == "POL-006": # High Risk -> Human Review
        selection_method = "High-Risk Mandatory Escalation"
        if request.risk_level in ["HIGH", "CRITICAL"]:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            policy_selected_winner_id = None
            policy_selected_winner_name = None

    elif policy_id == "POL-007": # Minimum Confidence Threshold
        selection_method = "Minimum Confidence Threshold"
        threshold = policy.min_confidence_threshold * 100.0
        if top_confidence < threshold:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            policy_selected_winner_id = None
            policy_selected_winner_name = None

    elif policy_id == "POL-008": # Consensus Required
        selection_method = "Consensus Threshold (75%)"
        consensus_pct = max_agree_count / total_models
        if consensus_pct < 0.75:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            policy_selected_winner_id = None
            policy_selected_winner_name = None

    elif policy_id == "POL-009": # Two-Model Agreement
        selection_method = "Two-Model Minimum Agreement"
        if max_agree_count < 2:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            policy_selected_winner_id = None
            policy_selected_winner_name = None

    elif policy_id == "POL-010": # Risk-Based Governance
        selection_method = "Risk-Based Tiered Governance"

    # 3. General Risk Level Governance Checks
    if not human_review_required:
        if request.risk_level == "CRITICAL" and len(decisions_group) > 1:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            policy_selected_winner_id = None
            policy_selected_winner_name = None
            selection_method += " (Critical Risk Escalated)"

        elif request.risk_level == "HIGH" and max_agree_count < 2:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            policy_selected_winner_id = None
            policy_selected_winner_name = None
            selection_method += " (High Risk Escalated)"

        elif request.risk_level == "MEDIUM" and top_confidence < 80.0:
            human_review_required = True
            final_decision_str = "PENDING HUMAN REVIEW"
            policy_selected_winner_id = None
            policy_selected_winner_name = None
            selection_method += " (Medium Risk Low-Confidence Escalated)"

    # 4. Policy Override & Override Rationale Determination
    if human_review_required:
        policy_override = True
        override_reason = f"Active governance policy '{policy.policy_name}' ({selection_method}) mandated escalation to human review due to risk constraints or model disagreement."
    elif (policy_selected_winner_name != weighted_score_winner_name) or (final_decision_str != top_weighted_response.decision):
        policy_override = True
        override_reason = f"Active policy '{policy.policy_name}' ({selection_method}) selected '{policy_selected_winner_name}' ({final_decision_str}) even though '{weighted_score_winner_name}' achieved the highest raw weighted arbitration score ({round(top_weighted_score, 1)}/100)."
    else:
        policy_override = False
        override_reason = f"None - Weighted score winner '{weighted_score_winner_name}' aligns with active policy '{policy.policy_name}' ({selection_method}) decision."

    # 5. Formulate 10-Point Comprehensive Explanation Text
    models_summary = ", ".join([
        f"{item['model_name']}: {item['decision']} (Conf: {item['confidence']}%, Rel: {item['reliability']}%, Cost: ${item['cost_per_request']:.3f}, Score: {item['arbitration_score']})"
        for item in scores_breakdown
    ])

    explanation_parts = [
        f"[Model Outputs]: {models_summary}.",
        f"[Selected Policy]: {policy.policy_name} (Method: {selection_method}).",
        f"[Weighted Score Winner]: {weighted_score_winner_name} (Score: {round(top_weighted_score, 1)}/100).",
        f"[Policy Selected Winner]: {policy_selected_winner_name if policy_selected_winner_name else 'None (Escalated)'}.",
        f"[Final Decision]: {final_decision_str}.",
        f"[Policy Override]: {'YES' if policy_override else 'NO'} ({override_reason}).",
        f"[Governance & Risk]: Risk Level = {request.risk_level}, Human Review Required = {human_review_required}."
    ]
    explanation = " ".join(explanation_parts)

    final_winning_model_name = policy_selected_winner_name if not human_review_required else None
    final_winning_model_id = policy_selected_winner_id if not human_review_required else None

    return {
        "request_id": request.request_id,
        "final_decision": final_decision_str,
        "winning_model": final_winning_model_name,
        "winning_model_id": final_winning_model_id,
        "weighted_score_winner": weighted_score_winner_name,
        "weighted_score_winner_id": weighted_score_winner_id,
        "policy_selected_winner": policy_selected_winner_name,
        "policy_selected_winner_id": policy_selected_winner_id,
        "selection_method": selection_method,
        "policy_override": policy_override,
        "override_reason": override_reason,
        "total_cost": total_cost,
        "arbitration_score": round(top_weighted_score, 2),
        "confidence": round(top_confidence, 1),
        "risk_level": request.risk_level,
        "policy_used": policy.policy_name,
        "models_considered": total_models,
        "agreement_level": agreement_level,
        "explanation": explanation,
        "human_review_required": human_review_required,
        "scores_breakdown": scores_breakdown
    }
