from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import AIModel
from app.schemas import AIModelCreate, AIModelUpdate, AIModelResponse

router = APIRouter(prefix="/api/models", tags=["AI Models"])

@router.get("", response_model=List[AIModelResponse])
def get_models(db: Session = Depends(get_db)):
    return db.query(AIModel).all()

@router.post("", response_model=AIModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(model_in: AIModelCreate, db: Session = Depends(get_db)):
    existing = db.query(AIModel).filter(AIModel.model_id == model_in.model_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Model ID {model_in.model_id} already exists.")
    
    model = AIModel(**model_in.dict())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

@router.put("/{model_id}", response_model=AIModelResponse)
def update_model(model_id: str, model_in: AIModelUpdate, db: Session = Depends(get_db)):
    model = db.query(AIModel).filter(AIModel.model_id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found.")
    
    for key, val in model_in.dict(exclude_unset=True).items():
        if val is not None:
            setattr(model, key, val)
            
    db.commit()
    db.refresh(model)
    return model
