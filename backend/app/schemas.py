from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Vendor Schemas ---
class VendorBase(BaseModel):
    vendor_id: str
    vendor_name: str
    description: Optional[str] = None
    status: str = "Active"
    reliability_score: float = 0.90
    average_latency: int = 500
    total_requests: int = 0
    successful_requests: int = 0

class VendorCreate(VendorBase):
    pass

class VendorResponse(VendorBase):
    id: int
    class Config:
        from_attributes = True

# --- Model Schemas ---
class AIModelBase(BaseModel):
    model_id: str
    model_name: str
    vendor_id: str
    version: str = "v1.0"
    accuracy_score: float = 0.90
    confidence_score: float = 0.88
    reliability_score: float = 0.92
    cost_per_request: float = 0.010
    latency_ms: int = 600
    status: str = "Active"
    total_decisions: int = 0

class AIModelCreate(AIModelBase):
    pass

class AIModelUpdate(BaseModel):
    model_name: Optional[str] = None
    version: Optional[str] = None
    accuracy_score: Optional[float] = None
    confidence_score: Optional[float] = None
    reliability_score: Optional[float] = None
    cost_per_request: Optional[float] = None
    latency_ms: Optional[int] = None
    status: Optional[str] = None

class AIModelResponse(AIModelBase):
    id: int
    class Config:
        from_attributes = True

# --- Model Response Schemas ---
class ModelResponseItemBase(BaseModel):
    response_id: str
    request_id: str
    model_id: str
    decision: str # APPROVE, REJECT, REVIEW
    confidence: float
    reasoning_summary: str
    processing_time: int
    timestamp: datetime

class ModelResponseItemResponse(ModelResponseItemBase):
    model_name: Optional[str] = None
    cost_per_request: Optional[float] = 0.010
    class Config:
        from_attributes = True

# --- Decision Request Schemas ---
class DecisionRequestCreate(BaseModel):
    request_type: str
    applicant_id: str
    description: str
    priority: str = "Medium" # Low, Medium, High
    risk_level: str = "MEDIUM" # LOW, MEDIUM, HIGH, CRITICAL
    selected_models: Optional[List[str]] = None # Model IDs to run against

class DecisionRequestResponse(BaseModel):
    id: int
    request_id: str
    request_type: str
    applicant_id: str
    description: str
    priority: str
    risk_level: str
    submitted_date: datetime
    status: str
    final_decision: Optional[str] = None
    responses: List[ModelResponseItemResponse] = []
    class Config:
        from_attributes = True

# --- Policy Schemas ---
class ArbitrationPolicyBase(BaseModel):
    policy_id: str
    policy_name: str
    description: str
    is_active: bool = False
    min_confidence_threshold: float = 0.75
    consensus_required: bool = False
    weight_reliability: float = 0.30
    weight_confidence: float = 0.25
    weight_accuracy: float = 0.15
    weight_consensus: float = 0.15
    weight_cost: float = 0.15

class ArbitrationPolicyCreate(ArbitrationPolicyBase):
    pass

class ArbitrationPolicyUpdate(BaseModel):
    is_active: Optional[bool] = None
    min_confidence_threshold: Optional[float] = None
    consensus_required: Optional[bool] = None
    weight_reliability: Optional[float] = None
    weight_confidence: Optional[float] = None
    weight_accuracy: Optional[float] = None
    weight_consensus: Optional[float] = None
    weight_cost: Optional[float] = None

class ArbitrationPolicyResponse(ArbitrationPolicyBase):
    id: int
    created_date: datetime
    class Config:
        from_attributes = True

# --- Final Decision & Arbitration Run Schemas ---
class FinalDecisionResult(BaseModel):
    request_id: str
    final_decision: str
    winning_model: Optional[str] = None # Final policy-selected winner name
    winning_model_id: Optional[str] = None # Final policy-selected winner ID
    weighted_score_winner: Optional[str] = None
    weighted_score_winner_id: Optional[str] = None
    policy_selected_winner: Optional[str] = None
    policy_selected_winner_id: Optional[str] = None
    selection_method: str = "Weighted Scoring"
    policy_override: bool = False
    override_reason: Optional[str] = None
    total_cost: float = 0.0
    arbitration_score: float
    confidence: float
    risk_level: str
    policy_used: str
    models_considered: int
    agreement_level: str
    explanation: str
    human_review_required: bool
    timestamp: datetime
    model_outputs: List[Dict[str, Any]] = []
    scores_breakdown: List[Dict[str, Any]] = []

class RunArbitrationPayload(BaseModel):
    request_id: str
    policy_id: Optional[str] = None # Optional override, otherwise active policy is used

# --- Human Review Schemas ---
class HumanReviewAction(BaseModel):
    request_id: str
    action: str # APPROVE, REJECT, REQUEST_MORE_INFO
    reviewer_name: str
    notes: Optional[str] = ""

class HumanReviewResponseItem(BaseModel):
    id: int
    review_id: str
    request_id: str
    risk_level: str
    model_decisions: Any
    status: str
    human_decision: Optional[str]
    reviewer_name: Optional[str]
    review_notes: Optional[str]
    timestamp: datetime
    request_type: Optional[str] = None
    applicant_id: Optional[str] = None
    description: Optional[str] = None
    class Config:
        from_attributes = True

# --- Audit Log Schemas ---
class AuditLogResponseItem(BaseModel):
    id: int
    audit_id: str
    request_id: str
    timestamp: datetime
    models_used: str
    model_outputs: str
    policy_used: str
    scores: str
    final_decision: str
    winning_model: Optional[str] = None
    weighted_score_winner: Optional[str] = None
    policy_selected_winner: Optional[str] = None
    selection_method: Optional[str] = None
    policy_override: bool = False
    override_reason: Optional[str] = None
    risk_level: Optional[str] = None
    human_review: bool
    reviewer: Optional[str] = None
    reason: str
    class Config:
        from_attributes = True

# --- Analytics Summary Schemas ---
class AnalyticsSummary(BaseModel):
    total_decisions: int
    approved_count: int
    rejected_count: int
    pending_review_count: int
    average_confidence: float
    model_agreement_rate: float
    human_review_rate: float
    average_response_time: float
    decisions_by_status: Dict[str, int]
    decisions_by_model: Dict[str, int]
    model_accuracy: List[Dict[str, Any]]
    model_reliability: List[Dict[str, Any]]
    confidence_distribution: List[Dict[str, Any]]
    requests_over_time: List[Dict[str, Any]]
