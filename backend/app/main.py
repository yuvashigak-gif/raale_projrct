from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import vendors, models, decisions, policies, audit, human_review, analytics, scenarios

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Model Arbitration Layer API",
    description="Public Agency Decision Making Arbitration & Governance Engine",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(vendors.router)
app.include_router(models.router)
app.include_router(decisions.router)
app.include_router(policies.router)
app.include_router(audit.router)
app.include_router(human_review.router)
app.include_router(analytics.router)
app.include_router(scenarios.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "AI Model Arbitration Layer for Public Agency Decision Making",
        "simulation_mode": True,
        "api_docs": "/docs"
    }
