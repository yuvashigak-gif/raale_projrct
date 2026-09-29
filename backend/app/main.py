from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, DB_PATH
from app.routers import vendors, models, decisions, policies, audit, human_review, analytics, scenarios, experiment
import sqlite3

# Initialize DB tables
Base.metadata.create_all(bind=engine)

def ensure_db_schema():
    columns_to_add = [
        ('models', 'cost_per_request', 'REAL DEFAULT 0.010'),
        ('arbitration_policies', 'weight_cost', 'REAL DEFAULT 0.15'),
        ('final_decisions', 'weighted_score_winner_id', 'TEXT'),
        ('final_decisions', 'weighted_score_winner_name', 'TEXT'),
        ('final_decisions', 'policy_selected_winner_id', 'TEXT'),
        ('final_decisions', 'policy_selected_winner_name', 'TEXT'),
        ('final_decisions', 'selection_method', "TEXT DEFAULT 'Weighted Scoring'"),
        ('final_decisions', 'policy_override', 'BOOLEAN DEFAULT 0'),
        ('final_decisions', 'override_reason', 'TEXT'),
        ('final_decisions', 'total_cost', 'REAL DEFAULT 0.0'),
        ('audit_logs', 'weighted_score_winner', 'TEXT'),
        ('audit_logs', 'policy_selected_winner', 'TEXT'),
        ('audit_logs', 'selection_method', 'TEXT'),
        ('audit_logs', 'policy_override', 'BOOLEAN DEFAULT 0'),
        ('audit_logs', 'override_reason', 'TEXT'),
        ('audit_logs', 'risk_level', 'TEXT'),
    ]

    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        for table, col, col_type in columns_to_add:
            cursor.execute(f"PRAGMA table_info({table})")
            existing_cols = [r[1] for r in cursor.fetchall()]
            if col not in existing_cols:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Schema migration note: {e}")

ensure_db_schema()

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
app.include_router(experiment.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "AI Model Arbitration Layer for Public Agency Decision Making",
        "simulation_mode": True,
        "api_docs": "/docs"
    }
