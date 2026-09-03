# AI Model Arbitration Layer for Public Agency Decision Making

An enterprise-grade, policy-driven **AI Model Arbitration Platform** designed for public sector decision-making. When public agencies pilot multiple external AI models (e.g., OpenAI's GPT-5.6, Anthropic's Claude Sonnet, Google's Gemini, Microsoft's Azure AI Model, Cohere's Command R+) for requests such as permits, benefits eligibility, licensing, and environmental compliance, this platform evaluates conflicting model outputs using weighted multi-factor scoring, active arbitration policies, and risk-tier governance.

---

## Key Features

1. **Multi-Model Evaluation & Consensus**: Concurrently queries 3+ AI models per decision request and aggregates output decisions (`APPROVE`, `REJECT`, `REVIEW`).
2. **Weighted Scoring Arbitration Engine**:
   $$\text{Final Score} = (\text{Reliability} \times 0.35) + (\text{Confidence} \times 0.30) + (\text{Accuracy} \times 0.20) + (\text{Consensus} \times 0.15)$$
3. **10 Configurable Arbitration Policies**:
   - Majority Voting
   - Weighted Confidence
   - Highest Reliability
   - Weighted Reliability + Confidence (*Default Active*)
   - Human Review on Disagreement
   - High Risk → Human Review
   - Minimum Confidence Threshold
   - Consensus Required
   - Two-Model Agreement
   - Risk-Based Arbitration
4. **Risk Tier Governance (LOW, MEDIUM, HIGH, CRITICAL)**: Automated approvals for low risk; strict consensus & mandatory human oversight for high/critical risk.
5. **Human Review Queue**: Interactive pending review board allowing agency officers to review model recommendations, approve/reject/request info, and record justifications.
6. **Immutable Audit Trail**: Log of all raw model outputs, selected policies, score breakdowns, winning decisions, and human override notes.
7. **Simulation & Demo Mode**: Built-in simulated AI model engine with 8 preset demo scenarios to run reproducible offline demonstrations.
8. **Real-time Analytics Dashboard**: Interactive KPI metrics and charts tracking agreement rates, latency, confidence distribution, and model accuracy.

---

## Architecture & Technology Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, SQLAlchemy, SQLite Database.
- **Frontend**: React, Vite, Lucide Icons, Modern Glassmorphism CSS.
- **Storage**: SQLite (`arbitration.db`) with 20 Decision Requests, 60 Model Responses, 10 Policies, 5 Vendors, 5 Models, and 20 Audit Logs pre-seeded.

---

## How to Run the Application

### 1. Start the Backend Server
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
- Backend API will be live at: `http://localhost:8000`
- Interactive API Documentation: `http://localhost:8000/docs`

### 2. Start the Frontend Application
```bash
cd frontend
npm run dev
```
- Frontend Web App will be live at: `http://localhost:5173`

---

## Re-seeding Demo Data
To reset or re-seed the SQLite database with 20 decision requests and 60+ model outputs:
```bash
python backend/seed_data.py
```
