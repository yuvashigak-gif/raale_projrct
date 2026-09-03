from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import ArbitrationPolicy
from app.schemas import ArbitrationPolicyResponse, ArbitrationPolicyUpdate, ArbitrationPolicyCreate

router = APIRouter(prefix="/api/policies", tags=["Policies"])

@router.get("", response_model=List[ArbitrationPolicyResponse])
def get_policies(db: Session = Depends(get_db)):
    return db.query(ArbitrationPolicy).all()

@router.put("/{policy_id}/activate", response_model=ArbitrationPolicyResponse)
def activate_policy(policy_id: str, db: Session = Depends(get_db)):
    target = db.query(ArbitrationPolicy).filter(ArbitrationPolicy.policy_id == policy_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Policy not found.")
    
    # Deactivate all other policies
    db.query(ArbitrationPolicy).update({ArbitrationPolicy.is_active: False})
    target.is_active = True
    
    db.commit()
    db.refresh(target)
    return target

@router.put("/{policy_id}", response_model=ArbitrationPolicyResponse)
def update_policy(policy_id: str, policy_in: ArbitrationPolicyUpdate, db: Session = Depends(get_db)):
    policy = db.query(ArbitrationPolicy).filter(ArbitrationPolicy.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")
    
    for key, val in policy_in.dict(exclude_unset=True).items():
        if val is not None:
            setattr(policy, key, val)
            
    db.commit()
    db.refresh(policy)
    return policy
