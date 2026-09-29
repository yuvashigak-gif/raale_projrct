from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String, unique=True, index=True, nullable=False)
    vendor_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="Active") # Active, Inactive
    reliability_score = Column(Float, default=0.90) # 0.0 - 1.0
    average_latency = Column(Integer, default=500) # ms
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)

    models = relationship("AIModel", back_populates="vendor")

class AIModel(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String, unique=True, index=True, nullable=False)
    model_name = Column(String, nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.vendor_id"), nullable=False)
    version = Column(String, default="v1.0")
    accuracy_score = Column(Float, default=0.90) # 0.0 - 1.0
    confidence_score = Column(Float, default=0.88)
    reliability_score = Column(Float, default=0.92)
    cost_per_request = Column(Float, default=0.010) # Monetary cost per request ($)
    latency_ms = Column(Integer, default=600)
    status = Column(String, default="Active") # Active, Disabled
    total_decisions = Column(Integer, default=0)

    vendor = relationship("Vendor", back_populates="models")
    responses = relationship("ModelResponse", back_populates="model")

class DecisionRequest(Base):
    __tablename__ = "decision_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True, nullable=False)
    request_type = Column(String, nullable=False) # e.g. Permit Approval, Benefits Eligibility
    applicant_id = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="Medium") # Low, Medium, High
    risk_level = Column(String, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    submitted_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="In Progress") # In Progress, Completed, Pending Human Review
    final_decision = Column(String, nullable=True) # APPROVE, REJECT, REVIEW, PENDING

    responses = relationship("ModelResponse", back_populates="request", cascade="all, delete-orphan")
    final_decision_rel = relationship("FinalDecision", back_populates="request", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="request", cascade="all, delete-orphan")
    human_reviews = relationship("HumanReview", back_populates="request", cascade="all, delete-orphan")

class ModelResponse(Base):
    __tablename__ = "model_responses"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(String, unique=True, index=True, nullable=False)
    request_id = Column(String, ForeignKey("decision_requests.request_id"), nullable=False)
    model_id = Column(String, ForeignKey("models.model_id"), nullable=False)
    decision = Column(String, nullable=False) # APPROVE, REJECT, REVIEW
    confidence = Column(Float, nullable=False) # 0.0 - 1.0 or %
    reasoning_summary = Column(Text, nullable=False)
    processing_time = Column(Integer, default=500) # ms
    timestamp = Column(DateTime, default=datetime.utcnow)

    request = relationship("DecisionRequest", back_populates="responses")
    model = relationship("AIModel", back_populates="responses")

class ArbitrationPolicy(Base):
    __tablename__ = "arbitration_policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String, unique=True, index=True, nullable=False)
    policy_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    min_confidence_threshold = Column(Float, default=0.75) # 0.0 - 1.0
    consensus_required = Column(Boolean, default=False)
    weight_reliability = Column(Float, default=0.30)
    weight_confidence = Column(Float, default=0.25)
    weight_accuracy = Column(Float, default=0.15)
    weight_consensus = Column(Float, default=0.15)
    weight_cost = Column(Float, default=0.15)
    created_date = Column(DateTime, default=datetime.utcnow)

class FinalDecision(Base):
    __tablename__ = "final_decisions"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, ForeignKey("decision_requests.request_id"), unique=True, nullable=False)
    final_decision = Column(String, nullable=False) # APPROVE, REJECT, PENDING HUMAN REVIEW
    winning_model_id = Column(String, nullable=True) # Policy selected winner ID
    winning_model_name = Column(String, nullable=True) # Policy selected winner name
    weighted_score_winner_id = Column(String, nullable=True)
    weighted_score_winner_name = Column(String, nullable=True)
    policy_selected_winner_id = Column(String, nullable=True)
    policy_selected_winner_name = Column(String, nullable=True)
    selection_method = Column(String, default="Weighted Scoring")
    policy_override = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    total_cost = Column(Float, default=0.0)
    arbitration_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    policy_used = Column(String, nullable=False)
    models_considered = Column(Integer, default=3)
    agreement_level = Column(String, nullable=False) # e.g. "2 of 3 models"
    explanation = Column(Text, nullable=False)
    human_review_required = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    request = relationship("DecisionRequest", back_populates="final_decision_rel")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String, unique=True, index=True, nullable=False)
    request_id = Column(String, ForeignKey("decision_requests.request_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    models_used = Column(Text, nullable=False) # Comma separated or JSON string
    model_outputs = Column(Text, nullable=False) # JSON formatted string
    policy_used = Column(String, nullable=False)
    scores = Column(Text, nullable=False) # JSON formatted string
    final_decision = Column(String, nullable=False)
    winning_model = Column(String, nullable=True)
    weighted_score_winner = Column(String, nullable=True)
    policy_selected_winner = Column(String, nullable=True)
    selection_method = Column(String, nullable=True)
    policy_override = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    risk_level = Column(String, nullable=True)
    human_review = Column(Boolean, default=False)
    reviewer = Column(String, nullable=True)
    reason = Column(Text, nullable=False)

    request = relationship("DecisionRequest", back_populates="audit_logs")

class HumanReview(Base):
    __tablename__ = "human_reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String, unique=True, index=True, nullable=False)
    request_id = Column(String, ForeignKey("decision_requests.request_id"), nullable=False)
    risk_level = Column(String, nullable=False)
    model_decisions = Column(Text, nullable=False) # JSON representation
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED, MORE_INFO_REQUESTED
    human_decision = Column(String, nullable=True) # APPROVE, REJECT, REQUEST_MORE_INFO
    reviewer_name = Column(String, nullable=True)
    review_notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    request = relationship("DecisionRequest", back_populates="human_reviews")
