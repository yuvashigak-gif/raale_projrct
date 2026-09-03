# Project Documentation - AI Model Arbitration Layer for Public Agency Decision Making

## Abstract
Public sector agencies are increasingly adopting artificial intelligence to streamline administrative workflows, evaluate citizen applications, and approve public permits. However, relying on a single AI vendor introduces systemic vendor lock-in and single-point-of-failure risks. When agencies deploy multiple AI models concurrently, different models frequently yield contradictory decisions for identical inputs. This document details the engineering, mathematical formulation, system architecture, database schema, and operational workflows of the **AI Model Arbitration Layer**.

---

## 1. Problem Statement
When evaluating public requests (such as construction permit approvals, benefits eligibility assessments, and business license renewals), different external AI models produce conflicting recommendations:
- **Model A (GPT-5.6)**: `APPROVE` (Confidence: 94%)
- **Model B (Claude Sonnet)**: `APPROVE` (Confidence: 91%)
- **Model C (Gemini)**: `REJECT` (Confidence: 74%)

Without a structured arbitration protocol, public agencies face legal uncertainty, lack of explainability, and risk of improper automated decisions.

---

## 2. Proposed System Architecture

```
                 [ Public Agency Request ]
                             │
                             ▼
                  [ API Router Layer ]
                             │
                             ▼
              [ AI Model Simulation Layer ]
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
  (GPT-5.6)           (Claude Sonnet)          (Gemini)
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             ▼
             [ Weighted Arbitration Engine ]
                             │
             [ Policy Engine & Risk Evaluation ]
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
   (Auto Decision Finalized)    (Human Review Escalate)
              │                             │
              └──────────────┬──────────────┘
                             ▼
                  [ Immutable Audit Log ]
```

---

## 3. Mathematical Arbitration Algorithm

The platform evaluates each candidate model decision $D \in \{\text{APPROVE}, \text{REJECT}, \text{REVIEW}\}$ using a weighted multi-factor scoring equation:

$$S_i = \left( R_{\text{vendor}} \cdot w_{\text{rel}} + C_{\text{model}} \cdot w_{\text{conf}} + A_{\text{hist}} \cdot w_{\text{acc}} + \text{Consensus}_i \cdot w_{\text{cons}} \right) \times 100$$

Where:
- $R_{\text{vendor}}$: Historical reliability score of the AI vendor (0.0 – 1.0).
- $C_{\text{model}}$: Model self-reported confidence for the specific output (0.0 – 1.0).
- $A_{\text{hist}}$: Model historical accuracy benchmark (0.0 – 1.0).
- $\text{Consensus}_i$: Ratio of models recommending decision $D_i$ ($\frac{N_{\text{agreed}}}{N_{\text{total}}}$).
- $w_{\text{rel}}, w_{\text{conf}}, w_{\text{acc}}, w_{\text{cons}}$: Policy weight coefficients summing to 1.0.

---

## 4. Risk Level Governance Rules

1. **LOW Risk**: Automatic decision allowed if top score > threshold.
2. **MEDIUM Risk**: Automatic decision allowed if top model confidence $\ge 80\%$.
3. **HIGH Risk**: Strict consensus required ($\ge 75\%$ agreement); otherwise escalated to Human Review.
4. **CRITICAL Risk**: Mandatory escalation to Human Review Queue on any model disagreement or policy trigger.

---

## 5. Database Schema & Tables

- `vendors`: Vendor metadata, reliability scores, and latency metrics.
- `models`: Registered AI models, accuracy scores, and status.
- `decision_requests`: Agency decision requests with priority and risk tiers.
- `model_responses`: Individual model outputs, reasoning strings, and confidence levels.
- `arbitration_policies`: Policy definitions and weight configurations.
- `final_decisions`: Computed arbitration results, winning models, and explanations.
- `audit_logs`: Immutable governance log storing full JSON output payloads.
- `human_reviews`: Pending human review queue items and reviewer override notes.
