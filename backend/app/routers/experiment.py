from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ArbitrationPolicy
from app.experiment import run_baseline_vs_arbitration_experiment

router = APIRouter(prefix="/api/experiment", tags=["Baseline vs Arbitration Experiment"])

@router.get("/results")
def get_experiment_results(db: Session = Depends(get_db)):
    active_policy = db.query(ArbitrationPolicy).filter(ArbitrationPolicy.is_active == True).first()
    if not active_policy:
        active_policy = db.query(ArbitrationPolicy).first()
    return run_baseline_vs_arbitration_experiment(active_policy)

@router.post("/run")
def run_experiment_trigger(db: Session = Depends(get_db)):
    active_policy = db.query(ArbitrationPolicy).filter(ArbitrationPolicy.is_active == True).first()
    if not active_policy:
        active_policy = db.query(ArbitrationPolicy).first()
    return run_baseline_vs_arbitration_experiment(active_policy)
