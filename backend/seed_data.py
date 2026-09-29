import json
import random
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Vendor, AIModel, DecisionRequest, ModelResponse, ArbitrationPolicy, FinalDecision, AuditLog, HumanReview
from app.arbitration_engine import evaluate_arbitration

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data to re-seed cleanly
    db.query(AuditLog).delete()
    db.query(HumanReview).delete()
    db.query(FinalDecision).delete()
    db.query(ModelResponse).delete()
    db.query(DecisionRequest).delete()
    db.query(ArbitrationPolicy).delete()
    db.query(AIModel).delete()
    db.query(Vendor).delete()
    db.commit()

    print("Seeding Vendors...")
    vendors_data = [
        {"vendor_id": "V001", "vendor_name": "OpenAI", "description": "Leading artificial intelligence research laboratory and AI model developer.", "reliability_score": 0.94, "average_latency": 820, "status": "Active"},
        {"vendor_id": "V002", "vendor_name": "Anthropic", "description": "AI safety and research company specializing in reliable Claude foundation models.", "reliability_score": 0.92, "average_latency": 790, "status": "Active"},
        {"vendor_id": "V003", "vendor_name": "Google", "description": "Global technology vendor providing Gemini enterprise multimodal AI services.", "reliability_score": 0.89, "average_latency": 640, "status": "Active"},
        {"vendor_id": "V004", "vendor_name": "Microsoft", "description": "Enterprise cloud and AI service provider hosting Azure AI Decision Engine.", "reliability_score": 0.88, "average_latency": 710, "status": "Active"},
        {"vendor_id": "V005", "vendor_name": "Cohere", "description": "Enterprise AI platform offering Command series models for policy decisioning.", "reliability_score": 0.86, "average_latency": 680, "status": "Active"},
    ]

    for v in vendors_data:
        db.add(Vendor(**v))
    db.commit()

    print("Seeding AI Models...")
    models_data = [
        {"model_id": "M001", "model_name": "GPT-5.6", "vendor_id": "V001", "version": "v5.6-turbo", "accuracy_score": 0.95, "confidence_score": 0.92, "reliability_score": 0.94, "cost_per_request": 0.020, "latency_ms": 820, "status": "Active"},
        {"model_id": "M002", "model_name": "Claude Sonnet", "vendor_id": "V002", "version": "v3.7", "accuracy_score": 0.93, "confidence_score": 0.90, "reliability_score": 0.92, "cost_per_request": 0.015, "latency_ms": 790, "status": "Active"},
        {"model_id": "M003", "model_name": "Gemini", "vendor_id": "V003", "version": "v1.5-Pro", "accuracy_score": 0.91, "confidence_score": 0.87, "reliability_score": 0.89, "cost_per_request": 0.008, "latency_ms": 640, "status": "Active"},
        {"model_id": "M004", "model_name": "Azure AI Model", "vendor_id": "V004", "version": "v4.0", "accuracy_score": 0.89, "confidence_score": 0.85, "reliability_score": 0.88, "cost_per_request": 0.010, "latency_ms": 710, "status": "Active"},
        {"model_id": "M005", "model_name": "Command R+", "vendor_id": "V005", "version": "v2.1", "accuracy_score": 0.87, "confidence_score": 0.84, "reliability_score": 0.86, "cost_per_request": 0.005, "latency_ms": 680, "status": "Active"},
    ]

    for m in models_data:
        db.add(AIModel(**m))
    db.commit()

    print("Seeding 10 Arbitration Policies...")
    policies_data = [
        {"policy_id": "POL-001", "policy_name": "Majority Voting", "description": "Selects the decision supported by the highest number of participating AI models.", "is_active": False, "min_confidence_threshold": 0.70, "consensus_required": True, "weight_reliability": 0.20, "weight_confidence": 0.20, "weight_accuracy": 0.20, "weight_consensus": 0.25, "weight_cost": 0.15},
        {"policy_id": "POL-002", "policy_name": "Weighted Confidence", "description": "Aggregates confidence scores for each decision choice and selects the highest cumulative confidence option.", "is_active": False, "min_confidence_threshold": 0.75, "consensus_required": False, "weight_reliability": 0.15, "weight_confidence": 0.45, "weight_accuracy": 0.15, "weight_consensus": 0.10, "weight_cost": 0.15},
        {"policy_id": "POL-003", "policy_name": "Highest Reliability", "description": "Prioritizes the decision rendered by the AI model with the highest vendor reliability score.", "is_active": False, "min_confidence_threshold": 0.70, "consensus_required": False, "weight_reliability": 0.50, "weight_confidence": 0.15, "weight_accuracy": 0.10, "weight_consensus": 0.10, "weight_cost": 0.15},
        {"policy_id": "POL-004", "policy_name": "Weighted Reliability + Confidence", "description": "Standard multi-factor algorithm balancing vendor reliability (30%), model confidence (25%), accuracy (15%), consensus (15%), and monetary cost (15%).", "is_active": True, "min_confidence_threshold": 0.75, "consensus_required": False, "weight_reliability": 0.30, "weight_confidence": 0.25, "weight_accuracy": 0.15, "weight_consensus": 0.15, "weight_cost": 0.15},
        {"policy_id": "POL-005", "policy_name": "Human Review on Disagreement", "description": "Automatically escalates decision requests to human review whenever AI models produce non-unanimous recommendations.", "is_active": False, "min_confidence_threshold": 0.80, "consensus_required": True, "weight_reliability": 0.20, "weight_confidence": 0.20, "weight_accuracy": 0.20, "weight_consensus": 0.25, "weight_cost": 0.15},
        {"policy_id": "POL-006", "policy_name": "High Risk -> Human Review", "description": "Forces human-in-the-loop review for any request categorized under High or Critical risk levels.", "is_active": False, "min_confidence_threshold": 0.80, "consensus_required": True, "weight_reliability": 0.25, "weight_confidence": 0.25, "weight_accuracy": 0.20, "weight_consensus": 0.15, "weight_cost": 0.15},
        {"policy_id": "POL-007", "policy_name": "Minimum Confidence Threshold", "description": "Requires winning decision confidence to exceed 85%, otherwise routes to human review queue.", "is_active": False, "min_confidence_threshold": 0.85, "consensus_required": False, "weight_reliability": 0.20, "weight_confidence": 0.40, "weight_accuracy": 0.15, "weight_consensus": 0.10, "weight_cost": 0.15},
        {"policy_id": "POL-008", "policy_name": "Consensus Required", "description": "Requires minimum 75% agreement ratio among participating AI models to finalize automated decisions.", "is_active": False, "min_confidence_threshold": 0.75, "consensus_required": True, "weight_reliability": 0.20, "weight_confidence": 0.20, "weight_accuracy": 0.15, "weight_consensus": 0.30, "weight_cost": 0.15},
        {"policy_id": "POL-009", "policy_name": "Two-Model Agreement", "description": "Mandates that at least two AI models must explicitly agree on the recommendation before approval.", "is_active": False, "min_confidence_threshold": 0.75, "consensus_required": True, "weight_reliability": 0.20, "weight_confidence": 0.20, "weight_accuracy": 0.20, "weight_consensus": 0.25, "weight_cost": 0.15},
        {"policy_id": "POL-010", "policy_name": "Risk-Based Arbitration", "description": "Applies tiered governance: Low Risk -> Auto approval, Medium -> >80% confidence auto, High -> Consensus, Critical -> Mandatory Human Review.", "is_active": False, "min_confidence_threshold": 0.80, "consensus_required": True, "weight_reliability": 0.25, "weight_confidence": 0.25, "weight_accuracy": 0.20, "weight_consensus": 0.15, "weight_cost": 0.15},
    ]

    for p in policies_data:
        db.add(ArbitrationPolicy(**p))
    db.commit()

    print("Seeding 20 Public Agency Decision Requests...")
    requests_data = [
        {"request_id": "DR001", "request_type": "Permit Approval", "applicant_id": "APP1001", "description": "Construction permit application for residential development on Elm Street.", "priority": "High", "risk_level": "MEDIUM"},
        {"request_id": "DR002", "request_type": "Benefits Eligibility", "applicant_id": "APP1002", "description": "Applicant requests eligibility assessment for public assistance and Medicaid benefits.", "priority": "Medium", "risk_level": "LOW"},
        {"request_id": "DR003", "request_type": "License Renewal", "applicant_id": "APP1003", "description": "Commercial food service business license renewal request for Downtown Cafe.", "priority": "Low", "risk_level": "LOW"},
        {"request_id": "DR004", "request_type": "Environmental Approval", "applicant_id": "APP1004", "description": "Industrial project environmental compliance assessment for Riverbank Manufacturing.", "priority": "High", "risk_level": "HIGH"},
        {"request_id": "DR005", "request_type": "Infrastructure Funding", "applicant_id": "APP1005", "description": "Application for municipal infrastructure grant funding for Eastside Transit Line.", "priority": "High", "risk_level": "HIGH"},
        {"request_id": "DR006", "request_type": "Zoning Exception", "applicant_id": "APP1006", "description": "Commercial zoning setback exemption request for solar panel installation.", "priority": "Low", "risk_level": "LOW"},
        {"request_id": "DR007", "request_type": "Public Health Grant", "applicant_id": "APP1007", "description": "Community health center operating grant eligibility evaluation.", "priority": "Medium", "risk_level": "MEDIUM"},
        {"request_id": "DR008", "request_type": "Hazardous Materials License", "applicant_id": "APP1008", "description": "Special permit for transporting medical isotope waste materials across state borders.", "priority": "High", "risk_level": "CRITICAL"},
        {"request_id": "DR009", "request_type": "Housing Subsidy", "applicant_id": "APP1009", "description": "Section 8 tenant-based rental voucher approval request.", "priority": "Medium", "risk_level": "LOW"},
        {"request_id": "DR010", "request_type": "Water Discharge Permit", "applicant_id": "APP1010", "description": "Agricultural runoff treatment discharge compliance review for Valley Farms.", "priority": "High", "risk_level": "HIGH"},
        {"request_id": "DR011", "request_type": "Vendor Contracting", "applicant_id": "APP1011", "description": "Municipal IT cloud infrastructure procurement vendor eligibility check.", "priority": "Medium", "risk_level": "MEDIUM"},
        {"request_id": "DR012", "request_type": "Liquor License Renewal", "applicant_id": "APP1012", "description": "Annual renewal for On-Premise Spirits Consumption at Metro Lounge.", "priority": "Low", "risk_level": "LOW"},
        {"request_id": "DR013", "request_type": "Disaster Relief Grant", "applicant_id": "APP1013", "description": "Small business flood emergency recovery grant application.", "priority": "High", "risk_level": "MEDIUM"},
        {"request_id": "DR014", "request_type": "Building Demolition", "applicant_id": "APP1014", "description": "Historic district structure demolition and site clearance permit.", "priority": "High", "risk_level": "HIGH"},
        {"request_id": "DR015", "request_type": "Childcare Facility Permit", "applicant_id": "APP1015", "description": "Safety clearance and occupancy certification for Sunshine Early Learning.", "priority": "High", "risk_level": "HIGH"},
        {"request_id": "DR016", "request_type": "Public Utility Connection", "applicant_id": "APP1016", "description": "High-voltage industrial electrical grid expansion clearance.", "priority": "Medium", "risk_level": "MEDIUM"},
        {"request_id": "DR017", "request_type": "Tax Exemption Request", "applicant_id": "APP1017", "description": "Non-profit community foundation property tax exemption filing.", "priority": "Low", "risk_level": "LOW"},
        {"request_id": "DR018", "request_type": "Port Facility Operations", "applicant_id": "APP1018", "description": "Maritime cargo handling expansion permit and noise impact review.", "priority": "High", "risk_level": "CRITICAL"},
        {"request_id": "DR019", "request_type": "Telecommunications Tower", "applicant_id": "APP1019", "description": "5G microcell antenna installation on municipal light poles.", "priority": "Medium", "risk_level": "LOW"},
        {"request_id": "DR020", "request_type": "Public Transport Access", "applicant_id": "APP1020", "description": "ADA compliance certification for remodeled subway transit terminal.", "priority": "High", "risk_level": "MEDIUM"},
    ]

    base_time = datetime.utcnow() - timedelta(days=10)

    # Specific preset model responses seed per request (to create realistic varied scenarios)
    preset_response_scenarios = [
        # DR001: Approve 2, Review 1 -> Approve
        [("M001", "APPROVE", 92, "Zoning setback and building height meet city standards."), ("M002", "APPROVE", 88, "Traffic impact study within threshold limits."), ("M003", "REVIEW", 76, "Soil stability test details require minor clarification.")],
        # DR002: Approve 3 -> Unanimous
        [("M001", "APPROVE", 95, "Applicant household income satisfies low-income criteria."), ("M002", "APPROVE", 93, "Identity and residency documents fully validated."), ("M003", "APPROVE", 91, "No duplicate benefit claims detected in system.")],
        # DR003: Approve 3 -> Unanimous
        [("M001", "APPROVE", 96, "Health inspection grade A (98/100). License renewal approved."), ("M002", "APPROVE", 94, "All municipal fees paid in full."), ("M004", "APPROVE", 90, "Fire marshal clearance valid.")],
        # DR004: Reject 2, Approve 1 -> Reject
        [("M001", "REJECT", 94, "Water discharge parameters exceed maximum EPA limits."), ("M002", "REJECT", 91, "Missing critical air quality mitigation plan."), ("M003", "APPROVE", 78, "Economic impact report favors industrial expansion.")],
        # DR005: Approve 2, Reject 1 -> Approve
        [("M001", "APPROVE", 91, "Project ROI and municipal transit benefits verified."), ("M002", "APPROVE", 89, "Engineering structural plans meet DOT standards."), ("M005", "REJECT", 72, "Grant requested exceeds standard regional allocation cap.")],
        # DR006: Approve 3 -> Unanimous
        [("M001", "APPROVE", 93, "Rooftop solar variance complies with green energy ordinance."), ("M002", "APPROVE", 90, "No visual obstruction for neighboring properties."), ("M003", "APPROVE", 88, "Electrical grid integration pre-approved.")],
        # DR007: Approve 2, Review 1 -> Approve
        [("M001", "APPROVE", 89, "Community service reach matches grant target objectives."), ("M002", "REVIEW", 75, "Budget allocation breakdown needs granular line items."), ("M004", "APPROVE", 87, "Audited financial statements verified clean.")],
        # DR008: CRITICAL RISK -> Approve 2, Reject 1 -> Human Review
        [("M001", "APPROVE", 91, "Transport route avoids major populated school zones."), ("M002", "APPROVE", 88, "Hazmat containment vessel meets federal specs."), ("M003", "REJECT", 86, "Proximity to wildlife watershed requires manual site inspection.")],
        # DR009: Approve 3 -> Unanimous
        [("M001", "APPROVE", 94, "Family size and income ratio verified for voucher."), ("M002", "APPROVE", 92, "Landlord agreement terms standard."), ("M005", "APPROVE", 89, "Background check passed.")],
        # DR010: HIGH RISK -> Reject 2, Approve 1 -> Reject / Review
        [("M001", "REJECT", 92, "Nitrate runoff levels exceed safe drinking water limits."), ("M002", "REJECT", 89, "Inadequate bio-retention pond capacity."), ("M003", "APPROVE", 81, "Proposed buffer strip meets basic guidelines.")],
        # DR011: Approve 3 -> Unanimous
        [("M001", "APPROVE", 90, "FedRAMP certification verified."), ("M002", "APPROVE", 88, "SOC 2 Type II audit clean."), ("M004", "APPROVE", 92, "Competitive pricing score high.")],
        # DR012: Approve 3 -> Unanimous
        [("M001", "APPROVE", 97, "No police violations reported past 24 months."), ("M002", "APPROVE", 95, "State tax compliance current."), ("M003", "APPROVE", 93, "Liquor board renewal fee paid.")],
        # DR013: Approve 2, Review 1 -> Approve
        [("M001", "APPROVE", 90, "Flood damage assessment verified by FEMA imagery."), ("M002", "APPROVE", 87, "Business continuity plan active."), ("M005", "REVIEW", 74, "Insurance claim settlement copy pending.")],
        # DR014: HIGH RISK -> Reject 2, Review 1 -> Human Review
        [("M001", "REJECT", 89, "Historic landmark preservation evaluation negative."), ("M002", "REJECT", 86, "Structural engineer recommends remediation over demolition."), ("M003", "REVIEW", 71, "Public hearing feedback uncompiled.")],
        # DR015: HIGH RISK -> Approve 2, Review 1 -> Human Review
        [("M001", "APPROVE", 91, "Background checks complete for all staffing list."), ("M002", "APPROVE", 89, "Fire evacuation plan passes code."), ("M004", "REVIEW", 79, "Playground equipment safety certificate pending physical inspection.")],
        # DR016: Approve 3 -> Unanimous
        [("M001", "APPROVE", 93, "Substation capacity sufficient for load extension."), ("M002", "APPROVE", 91, "Transformer safety specs compliant."), ("M005", "APPROVE", 87, "Environmental electromagnetic clearance granted.")],
        # DR017: Approve 3 -> Unanimous
        [("M001", "APPROVE", 95, "501(c)(3) active status verified with IRS database."), ("M002", "APPROVE", 94, "Property usage strictly dedicated to charitable purposes."), ("M003", "APPROVE", 92, "Annual reporting up to date.")],
        # DR018: CRITICAL RISK -> Approve 2, Reject 1 -> Human Review
        [("M001", "APPROVE", 88, "Port berth depth dredging meets harbor guidelines."), ("M002", "REJECT", 87, "Acoustic underwater noise impact exceeds marine safety threshold."), ("M004", "APPROVE", 85, "Economic trade volume model strongly favorable.")],
        # DR019: Approve 3 -> Unanimous
        [("M001", "APPROVE", 92, "RF radiation output within FCC safety limits."), ("M002", "APPROVE", 90, "Light pole structural weight load calculation acceptable."), ("M003", "APPROVE", 89, "Co-location agreement compliant.")],
        # DR020: Approve 2, Review 1 -> Approve
        [("M001", "APPROVE", 93, "Wheelchair ramp gradient matches 1:12 ADA standard."), ("M002", "APPROVE", 91, "Braille signage installed at all passenger gates."), ("M005", "REVIEW", 77, "Audio announcement decibel calibration check pending.")],
    ]

    active_policy = db.query(ArbitrationPolicy).filter(ArbitrationPolicy.is_active == True).first()
    models_dict = {m.model_id: m for m in db.query(AIModel).all()}

    audit_counter = 1

    for idx, r_data in enumerate(requests_data):
        submitted_time = base_time + timedelta(hours=idx * 12)
        req = DecisionRequest(
            request_id=r_data["request_id"],
            request_type=r_data["request_type"],
            applicant_id=r_data["applicant_id"],
            description=r_data["description"],
            priority=r_data["priority"],
            risk_level=r_data["risk_level"],
            submitted_date=submitted_time,
            status="In Progress",
            final_decision="PENDING"
        )
        db.add(req)
        db.commit()

        # Seed model responses
        resp_specs = preset_response_scenarios[idx]
        saved_resps = []
        for r_idx, (m_id, dec, conf, reason) in enumerate(resp_specs):
            m_resp = ModelResponse(
                response_id=f"RESP-{r_data['request_id']}-{r_idx+1}",
                request_id=r_data["request_id"],
                model_id=m_id,
                decision=dec,
                confidence=conf,
                reasoning_summary=reason,
                processing_time=random.randint(600, 920),
                timestamp=submitted_time + timedelta(seconds=r_idx * 2)
            )
            db.add(m_resp)
            saved_resps.append(m_resp)
        db.commit()

        # Evaluate arbitration
        arbitration_res = evaluate_arbitration(req, saved_resps, models_dict, active_policy)

        # Save Final Decision
        final_dec = FinalDecision(
            request_id=r_data["request_id"],
            final_decision=arbitration_res["final_decision"],
            winning_model_id=arbitration_res["winning_model_id"],
            winning_model_name=arbitration_res["winning_model"],
            weighted_score_winner_id=arbitration_res["weighted_score_winner_id"],
            weighted_score_winner_name=arbitration_res["weighted_score_winner"],
            policy_selected_winner_id=arbitration_res["policy_selected_winner_id"],
            policy_selected_winner_name=arbitration_res["policy_selected_winner"],
            selection_method=arbitration_res["selection_method"],
            policy_override=arbitration_res["policy_override"],
            override_reason=arbitration_res["override_reason"],
            total_cost=arbitration_res["total_cost"],
            arbitration_score=arbitration_res["arbitration_score"],
            confidence=arbitration_res["confidence"],
            risk_level=arbitration_res["risk_level"],
            policy_used=arbitration_res["policy_used"],
            models_considered=arbitration_res["models_considered"],
            agreement_level=arbitration_res["agreement_level"],
            explanation=arbitration_res["explanation"],
            human_review_required=arbitration_res["human_review_required"],
            timestamp=submitted_time + timedelta(seconds=10)
        )
        db.add(final_dec)

        if arbitration_res["human_review_required"]:
            req.status = "Pending Human Review"
            req.final_decision = "PENDING HUMAN REVIEW"

            h_review = HumanReview(
                review_id=f"HR-{r_data['request_id']}",
                request_id=r_data["request_id"],
                risk_level=req.risk_level,
                model_decisions=json.dumps([
                    {"model": models_dict.get(r.model_id).model_name if models_dict.get(r.model_id) else r.model_id, "decision": r.decision, "confidence": r.confidence}
                    for r in saved_resps
                ]),
                status="PENDING",
                timestamp=submitted_time + timedelta(seconds=12)
            )
            db.add(h_review)
        else:
            req.status = "Completed"
            req.final_decision = arbitration_res["final_decision"]

        # Audit Log entry
        audit = AuditLog(
            audit_id=f"AUD-{audit_counter:04d}",
            request_id=r_data["request_id"],
            timestamp=submitted_time + timedelta(seconds=15),
            models_used=",".join([r.model_id for r in saved_resps]),
            model_outputs=json.dumps([
                {"model_id": r.model_id, "decision": r.decision, "confidence": r.confidence, "reason": r.reasoning_summary}
                for r in saved_resps
            ]),
            policy_used=active_policy.policy_name,
            scores=json.dumps(arbitration_res["scores_breakdown"]),
            final_decision=arbitration_res["final_decision"],
            winning_model=arbitration_res["winning_model"],
            weighted_score_winner=arbitration_res["weighted_score_winner"],
            policy_selected_winner=arbitration_res["policy_selected_winner"],
            selection_method=arbitration_res["selection_method"],
            policy_override=arbitration_res["policy_override"],
            override_reason=arbitration_res["override_reason"],
            risk_level=req.risk_level,
            human_review=arbitration_res["human_review_required"],
            reviewer="ArbitrationEngine" if not arbitration_res["human_review_required"] else None,
            reason=arbitration_res["explanation"]
        )
        db.add(audit)
        audit_counter += 1
        db.commit()

    print("Seed process completed successfully!")
    print(f"Total Decision Requests: {db.query(DecisionRequest).count()}")
    print(f"Total Model Responses: {db.query(ModelResponse).count()}")
    print(f"Total Final Decisions: {db.query(FinalDecision).count()}")
    print(f"Total Audit Logs: {db.query(AuditLog).count()}")
    print(f"Pending Human Reviews: {db.query(HumanReview).count()}")
    db.close()

if __name__ == "__main__":
    seed_database()
