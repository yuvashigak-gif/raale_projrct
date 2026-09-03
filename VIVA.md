# Viva & Presentation Explanation Guide

## 1. Simple Explanation of the Project

"Three AI models give their opinions on a public agency request.
The arbitration engine does not blindly trust any single model.
It calculates a composite score using vendor reliability, model confidence, historical accuracy, and agreement consensus.
The recommendation supported by the strongest overall evidence is selected.
If the system is uncertain or the request is high risk, it sends the case to a human reviewer for final sign-off while saving a complete audit record."

---

## 2. Frequently Asked Viva Questions & Answers

### Q1: Why do public agencies need an AI Model Arbitration Layer?
**Answer**: Public agencies cannot rely on a single proprietary AI model due to vendor lock-in, outage risks, and potential algorithmic bias. When using multiple models, conflicting outputs occur. An arbitration layer provides structured consensus resolution, policy governance, and legal auditability.

### Q2: Why can't we simply use a basic majority vote?
**Answer**: Majority voting treats all models as equal. In real-world AI deployments, models have different reliability ratings, historical accuracy, and confidence levels. For instance, a highly reliable model with 95% confidence should override two less reliable models with 60% confidence.

### Q3: How is the Arbitration Score calculated?
**Answer**:
$$\text{Score} = (\text{Reliability} \times 0.35) + (\text{Confidence} \times 0.30) + (\text{Accuracy} \times 0.20) + (\text{Consensus} \times 0.15)$$
Each model's output is evaluated against these weights to derive a normalized score from 0 to 100.

### Q4: How does the system handle High and Critical Risk requests?
**Answer**: The system enforces risk-tiered governance. Critical risk requests (e.g. hazardous material licenses) automatically trigger mandatory Human Review whenever models disagree, preventing automated errors on sensitive public matters.

### Q5: What is the purpose of the Audit Log?
**Answer**: In government and public sector applications, transparency and explainability are legally mandatory. The audit log records the exact input, raw model responses, policy used, mathematical scores, and human override notes.

---

## 3. Key Concepts Checklist for Viva

- [x] **Multi-Vendor AI Strategy**: Using models from OpenAI, Anthropic, Google, Microsoft, and Cohere.
- [x] **Weighted Scoring Formula**: Combining reliability, confidence, accuracy, and consensus.
- [x] **Configurable Policy Engine**: 10 distinct policies (Majority, Weighted Confidence, Risk-based, etc.).
- [x] **Human-in-the-Loop Governance**: Escalation queue for split decisions and high-risk cases.
- [x] **Simulation Mode**: Deterministic simulation engine enabling complete offline demonstration.
