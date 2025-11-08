from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.patient import Patient, PatientNarrative, ClinicalBriefing, EHRHistory
from app.schemas.patient import PatientResponse, PatientNarrativeResponse, ClinicalBriefingResponse, EHRHistoryBase

router = APIRouter()


@router.get("/patients", response_model=List[PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    """Get all patients with their briefing status"""
    patients = db.query(Patient).all()

    result = []
    for patient in patients:
        # Check if patient has a briefing
        has_briefing = db.query(ClinicalBriefing).filter(
            ClinicalBriefing.patient_id == patient.patient_id
        ).first() is not None

        result.append({
            "patient_id": patient.patient_id,
            "full_name": patient.full_name,
            "date_of_birth": patient.date_of_birth,
            "gender_identity": patient.gender_identity,
            "race": patient.race,
            "address_zip_code": patient.address_zip_code,
            "briefing_status": "Briefing Ready" if has_briefing else "Pending Intake"
        })

    return result


@router.get("/patients/{patient_id}/narratives", response_model=List[PatientNarrativeResponse])
def get_patient_narratives(patient_id: str, db: Session = Depends(get_db)):
    """Get all narratives for a specific patient"""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    narratives = db.query(PatientNarrative).filter(
        PatientNarrative.patient_id == patient_id
    ).all()

    return narratives


@router.get("/patients/{patient_id}/briefing", response_model=ClinicalBriefingResponse)
def get_patient_briefing(patient_id: str, db: Session = Depends(get_db)):
    """Get the clinical briefing for a specific patient"""
    briefing = db.query(ClinicalBriefing).filter(
        ClinicalBriefing.patient_id == patient_id
    ).first()

    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found for this patient")

    return briefing


@router.get("/patients/{patient_id}/ehr", response_model=EHRHistoryBase)
def get_patient_ehr(patient_id: str, db: Session = Depends(get_db)):
    """Get the EHR history for a specific patient"""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    ehr = db.query(EHRHistory).filter(
        EHRHistory.patient_id == patient_id
    ).first()

    if not ehr:
        raise HTTPException(status_code=404, detail="EHR history not found for this patient")

    return ehr
