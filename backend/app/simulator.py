import random
from typing import List, Dict, Any

MODELS_LIST = [
    {"model_id": "M001", "name": "GPT-5.6", "vendor": "OpenAI", "reliability": 0.94, "accuracy": 0.95, "cost": 0.020},
    {"model_id": "M002", "name": "Claude Sonnet", "vendor": "Anthropic", "reliability": 0.92, "accuracy": 0.93, "cost": 0.015},
    {"model_id": "M003", "name": "Gemini", "vendor": "Google", "reliability": 0.89, "accuracy": 0.91, "cost": 0.008},
    {"model_id": "M004", "name": "Azure AI Model", "vendor": "Microsoft", "reliability": 0.88, "accuracy": 0.89, "cost": 0.010},
    {"model_id": "M005", "name": "Command R+", "vendor": "Cohere", "reliability": 0.86, "accuracy": 0.87, "cost": 0.005},
]

PRESET_SCENARIOS = {
    "SCENARIO_1": {
        "name": "Unanimous Consensus (APPROVE)",
        "description": "All active models agree on APPROVE with high confidence.",
        "risk_level": "LOW",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 94, "reason": "Full compliance with municipal zoning laws and environmental requirements.", "latency": 780},
            {"model_id": "M002", "decision": "APPROVE", "confidence": 91, "reason": "Applicant documentation complete and verified against city standards.", "latency": 840},
            {"model_id": "M003", "decision": "APPROVE", "confidence": 88, "reason": "No policy conflicts found in submission.", "latency": 620},
        ]
    },
    "SCENARIO_2": {
        "name": "Unanimous Consensus (REJECT)",
        "description": "All active models agree on REJECT due to non-compliance.",
        "risk_level": "MEDIUM",
        "outcomes": [
            {"model_id": "M001", "decision": "REJECT", "confidence": 96, "reason": "Financial audit checks failed tax compliance criteria.", "latency": 810},
            {"model_id": "M002", "decision": "REJECT", "confidence": 93, "reason": "Missing required state environmental clearance certificates.", "latency": 760},
            {"model_id": "M003", "decision": "REJECT", "confidence": 90, "reason": "Applicant exceeded maximum allowed funding request thresholds.", "latency": 690},
        ]
    },
    "SCENARIO_3": {
        "name": "Split Decision (2 APPROVE + 1 REJECT)",
        "description": "Two models approve with high confidence while one model rejects.",
        "risk_level": "MEDIUM",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 92, "reason": "Primary qualifications and architectural designs satisfy all safety codes.", "latency": 830},
            {"model_id": "M002", "decision": "APPROVE", "confidence": 89, "reason": "Traffic impact study acceptable under urban development guidelines.", "latency": 870},
            {"model_id": "M003", "decision": "REJECT", "confidence": 74, "reason": "Minor zoning setbacks exceed recommended tolerance.", "latency": 710},
        ]
    },
    "SCENARIO_4": {
        "name": "Disagreement Split (1 APPROVE + 1 REJECT + 1 REVIEW)",
        "description": "Three models produce three different recommendations resulting in escalation.",
        "risk_level": "HIGH",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 82, "reason": "Income verification satisfies standard eligibility criteria.", "latency": 850},
            {"model_id": "M002", "decision": "REJECT", "confidence": 85, "reason": "Discrepancy detected in reported household asset declarations.", "latency": 790},
            {"model_id": "M003", "decision": "REVIEW", "confidence": 71, "reason": "Inconclusive proof of residency; manual document verification recommended.", "latency": 680},
        ]
    },
    "SCENARIO_5": {
        "name": "High Risk Request Escalation",
        "description": "High risk evaluation triggering policy review.",
        "risk_level": "HIGH",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 86, "reason": "Infrastructure feasibility study passes core engineering criteria.", "latency": 890},
            {"model_id": "M002", "decision": "REJECT", "confidence": 81, "reason": "Potential long-term environmental watershed risk identified.", "latency": 920},
            {"model_id": "M004", "decision": "APPROVE", "confidence": 84, "reason": "Economic impact model indicates positive municipal ROI.", "latency": 730},
        ]
    },
    "SCENARIO_6": {
        "name": "Low Confidence Model Outputs",
        "description": "Models return responses below acceptable confidence thresholds.",
        "risk_level": "MEDIUM",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 62, "reason": "Applicant history is sparse; probabilistic score favors approval.", "latency": 910},
            {"model_id": "M002", "decision": "REVIEW", "confidence": 65, "reason": "Insufficient OCR quality on scanned utility bill attachments.", "latency": 860},
            {"model_id": "M005", "decision": "APPROVE", "confidence": 59, "reason": "General business activity satisfies preliminary renewal terms.", "latency": 770},
        ]
    },
    "SCENARIO_7": {
        "name": "High Reliability Override",
        "description": "Top reliable model (GPT-5.6: 94% reliability) disagrees with lower reliability models.",
        "risk_level": "LOW",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 95, "reason": "Comprehensive cross-check confirms compliance with state regulations.", "latency": 800},
            {"model_id": "M004", "decision": "REJECT", "confidence": 71, "reason": "Flagged non-critical administrative formality.", "latency": 750},
            {"model_id": "M005", "decision": "REJECT", "confidence": 68, "reason": "Potential ambiguity in secondary business registration documents.", "latency": 710},
        ]
    },
    "SCENARIO_8": {
        "name": "Critical Request Mandatory Review",
        "description": "Critical public safety request requiring mandatory human oversight.",
        "risk_level": "CRITICAL",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 91, "reason": "Hazardous material disposal protocol meets safety threshold.", "latency": 880},
            {"model_id": "M002", "decision": "APPROVE", "confidence": 88, "reason": "Secondary safety containment specs pass simulation modeling.", "latency": 940},
            {"model_id": "M003", "decision": "REJECT", "confidence": 86, "reason": "Proximity to protected wildlife sanctuary requires expert site inspection.", "latency": 810},
        ]
    },
    # --- EDGE / FAILURE CASES ---
    "EDGE_CASE_1": {
        "name": "Edge Case 1: Model API Failure / Single Active Response",
        "description": "System experiences API timeout; only 1 model responds. Engine safely mandates Human Review.",
        "risk_level": "MEDIUM",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 92, "reason": "Only 1 AI model returned response due to upstream API network failure.", "latency": 1200}
        ]
    },
    "EDGE_CASE_2": {
        "name": "Edge Case 2: 100% Conflicting Model Decisions",
        "description": "Model outputs disagree completely (1 APPROVE, 1 REJECT, 1 REVIEW). Engine escalates to Human Review queue.",
        "risk_level": "HIGH",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 91, "reason": "Financial audit passed core thresholds.", "latency": 820},
            {"model_id": "M002", "decision": "REJECT", "confidence": 89, "reason": "Zoning clearance failed setback requirements.", "latency": 850},
            {"model_id": "M003", "decision": "REVIEW", "confidence": 84, "reason": "Inconclusive applicant background check.", "latency": 780}
        ]
    },
    "EDGE_CASE_3": {
        "name": "Edge Case 3: High Cost vs Low Cost Model Balancing",
        "description": "Expensive model (GPT-5.6 $0.020) vs Low-cost model (Command R+ $0.005) with cost-weighted arbitration.",
        "risk_level": "LOW",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 91, "reason": "High cost GPT-5.6 model approves with 91% confidence.", "latency": 850},
            {"model_id": "M005", "decision": "REJECT", "confidence": 90, "reason": "Low cost Command R+ model rejects based on cost-effective heuristic.", "latency": 540}
        ]
    },
    "EDGE_CASE_4": {
        "name": "Edge Case 4: Low-Confidence High-Reliability vs High-Confidence Low-Reliability",
        "description": "M001 (Rel 94%, Conf 72%) vs M005 (Rel 86%, Conf 96%) tests policy weight trade-offs.",
        "risk_level": "MEDIUM",
        "outcomes": [
            {"model_id": "M001", "decision": "APPROVE", "confidence": 72, "reason": "Highly reliable model returns conservative approval.", "latency": 810},
            {"model_id": "M005", "decision": "REJECT", "confidence": 96, "reason": "Lower reliability model returns high confidence rejection.", "latency": 600}
        ]
    },
    "EDGE_CASE_5": {
        "name": "Edge Case 5: Missing / Invalid Payload Scores",
        "description": "Model returns payload with missing confidence. System applies fallback default score and audits transaction.",
        "risk_level": "MEDIUM",
        "outcomes": [
            {"model_id": "M002", "decision": "APPROVE", "confidence": 75, "reason": "Fallback default confidence applied due to missing confidence field.", "latency": 790},
            {"model_id": "M003", "decision": "APPROVE", "confidence": 88, "reason": "Standard valid model evaluation outcome.", "latency": 690}
        ]
    }
}

def generate_model_responses(request_id: str, scenario_key: str = None, selected_model_ids: List[str] = None) -> List[Dict[str, Any]]:
    """
    Generates realistic simulated model responses for a given request.
    """
    if scenario_key and scenario_key in PRESET_SCENARIOS:
        preset = PRESET_SCENARIOS[scenario_key]
        results = []
        for i, item in enumerate(preset["outcomes"]):
            results.append({
                "response_id": f"RESP-{request_id}-{i+1}",
                "request_id": request_id,
                "model_id": item["model_id"],
                "decision": item["decision"],
                "confidence": item["confidence"],
                "reasoning_summary": item["reason"],
                "processing_time": item["latency"]
            })
        return results

    # Default realistic generation
    models_to_use = selected_model_ids if selected_model_ids and len(selected_model_ids) >= 2 else ["M001", "M002", "M003"]
    results = []
    
    # Decide a baseline consensus direction
    decisions = ["APPROVE", "APPROVE", "APPROVE", "REJECT", "REVIEW"]
    primary_decision = random.choice(decisions)

    for i, m_id in enumerate(models_to_use):
        # 80% chance model aligns with primary decision, 20% chance variation
        dec = primary_decision if random.random() < 0.8 else random.choice(["APPROVE", "REJECT", "REVIEW"])
        conf = round(random.uniform(75.0, 96.0), 1)
        latency = random.randint(550, 950)
        
        reasons = {
            "APPROVE": "Submitted verification documents comply with agency regulatory standards and policy requirements.",
            "REJECT": "Critical documentation checks failed mandatory compliance threshold.",
            "REVIEW": "Inconclusive risk score detected; human review recommended for edge-case validation."
        }

        results.append({
            "response_id": f"RESP-{request_id}-{i+1}",
            "request_id": request_id,
            "model_id": m_id,
            "decision": dec,
            "confidence": conf,
            "reasoning_summary": reasons[dec],
            "processing_time": latency
        })

    return results
