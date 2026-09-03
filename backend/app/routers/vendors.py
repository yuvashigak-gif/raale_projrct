from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Vendor
from app.schemas import VendorCreate, VendorResponse

router = APIRouter(prefix="/api/vendors", tags=["Vendors"])

@router.get("", response_model=List[VendorResponse])
def get_vendors(db: Session = Depends(get_db)):
    return db.query(Vendor).all()

@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(vendor_in: VendorCreate, db: Session = Depends(get_db)):
    existing = db.query(Vendor).filter(Vendor.vendor_id == vendor_in.vendor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Vendor ID {vendor_in.vendor_id} already exists.")
    
    vendor = Vendor(**vendor_in.dict())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(vendor_id: str, vendor_in: VendorCreate, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found.")
    
    for key, val in vendor_in.dict(exclude_unset=True).items():
        setattr(vendor, key, val)
        
    db.commit()
    db.refresh(vendor)
    return vendor
