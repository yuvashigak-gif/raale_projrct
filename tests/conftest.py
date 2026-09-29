import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import (
    Vendor, AIModel, DecisionRequest, ModelResponse,
    ArbitrationPolicy, FinalDecision, AuditLog, HumanReview
)

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def sample_vendor(db_session):
    vendor = Vendor(
        vendor_id="V999",
        vendor_name="TestVendor Corp",
        description="Vendor for unit testing",
        reliability_score=0.95,
        average_latency=500,
        status="Active"
    )
    db_session.add(vendor)
    db_session.commit()
    return vendor

@pytest.fixture
def sample_models(db_session, sample_vendor):
    m1 = AIModel(
        model_id="M_HIGH_COST",
        model_name="GPT-Heavy",
        vendor_id=sample_vendor.vendor_id,
        version="v1.0",
        accuracy_score=0.95,
        confidence_score=0.92,
        reliability_score=0.94,
        cost_per_request=0.030,
        latency_ms=800,
        status="Active"
    )
    m2 = AIModel(
        model_id="M_LOW_COST",
        model_name="Gemini-Lite",
        vendor_id=sample_vendor.vendor_id,
        version="v1.0",
        accuracy_score=0.91,
        confidence_score=0.88,
        reliability_score=0.90,
        cost_per_request=0.005,
        latency_ms=400,
        status="Active"
    )
    m3 = AIModel(
        model_id="M_MID_REL",
        model_name="Claude-Standard",
        vendor_id=sample_vendor.vendor_id,
        version="v1.0",
        accuracy_score=0.93,
        confidence_score=0.90,
        reliability_score=0.92,
        cost_per_request=0.015,
        latency_ms=600,
        status="Active"
    )
    db_session.add_all([m1, m2, m3])
    db_session.commit()
    return {"M_HIGH_COST": m1, "M_LOW_COST": m2, "M_MID_REL": m3}

@pytest.fixture
def sample_policy(db_session):
    pol = ArbitrationPolicy(
        policy_id="POL-004",
        policy_name="Weighted Reliability + Confidence",
        description="Standard multi-factor policy",
        is_active=True,
        min_confidence_threshold=0.75,
        consensus_required=False,
        weight_reliability=0.30,
        weight_confidence=0.25,
        weight_accuracy=0.15,
        weight_consensus=0.15,
        weight_cost=0.15
    )
    db_session.add(pol)
    db_session.commit()
    return pol
