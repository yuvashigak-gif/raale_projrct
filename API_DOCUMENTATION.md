# API Documentation - AI Model Arbitration Layer

Base URL: `http://localhost:8000/api`

---

## 1. Vendors API

### `GET /api/vendors`
Retrieves all registered AI vendors.

### `POST /api/vendors`
Registers a new AI vendor.

---

## 2. AI Models API

### `GET /api/models`
Retrieves all registered AI models.

### `PUT /api/models/{model_id}`
Updates model status, accuracy, or reliability score.

---

## 3. Decision Requests & Arbitration API

### `GET /api/decisions`
Retrieves list of decision requests with optional query filters:
- `search`: String
- `risk`: LOW, MEDIUM, HIGH, CRITICAL
- `decision`: APPROVE, REJECT, PENDING HUMAN REVIEW

### `GET /api/decisions/{request_id}`
Fetches full decision details, model responses, arbitration score breakdown, and audit record.

### `POST /api/decisions`
Creates a new decision request, simulates model responses, runs the arbitration engine against the active policy, records an audit log entry, and returns the final decision.

---

## 4. Policy Engine API

### `GET /api/policies`
Lists all 10 arbitration policies.

### `PUT /api/policies/{policy_id}/activate`
Activates the specified policy across the arbitration engine.

---

## 5. Human Review API

### `GET /api/human-review`
Fetches all pending and completed human review items.

### `POST /api/human-review`
Submits a human officer decision (`APPROVE`, `REJECT`, `REQUEST_MORE_INFO`), updates request status, and records an audit log entry.

---

## 6. Demo Scenarios API

### `GET /api/scenarios`
Lists 8 preset evaluation scenarios.

### `POST /api/scenarios/run/{scenario_key}`
Executes a preset demo scenario and returns the live step-by-step arbitration result.
