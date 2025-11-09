from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from app.db.database import get_db
from app.models.patient import Patient, Appointment
from app.schemas.patient import (
    AppointmentResponse,
    AppointmentCreate,
    AppointmentUpdate
)

router = APIRouter()


@router.post("/appointments", response_model=AppointmentResponse, status_code=201)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new appointment for a patient"""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.patient_id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Generate appointment ID
    appointment_id = f"APT-{uuid.uuid4().hex[:10].upper()}"

    # Create appointment
    new_appointment = Appointment(
        appointment_id=appointment_id,
        patient_id=appointment.patient_id,
        appointment_date_time=appointment.appointment_date_time,
        appointment_status="scheduled",
        appointment_type=appointment.appointment_type,
        duration_minutes=appointment.duration_minutes,
        location=appointment.location,
        provider_name=appointment.provider_name,
        notes=appointment.notes
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


@router.get("/appointments", response_model=List[AppointmentResponse])
def get_appointments(
    patient_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get appointments with optional filters"""
    query = db.query(Appointment)

    # Filter by patient_id if provided
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)

    # Filter by status if provided
    if status:
        query = query.filter(Appointment.appointment_status == status)

    # Filter by date range if provided
    if start_date:
        query = query.filter(Appointment.appointment_date_time >= start_date)
    if end_date:
        query = query.filter(Appointment.appointment_date_time <= end_date)

    # Order by appointment date/time
    query = query.order_by(Appointment.appointment_date_time.asc())

    appointments = query.all()
    return appointments


@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific appointment by ID"""
    appointment = db.query(Appointment).filter(
        Appointment.appointment_id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return appointment


@router.get("/patients/{patient_id}/appointments", response_model=List[AppointmentResponse])
def get_patient_appointments(
    patient_id: str,
    status: Optional[str] = None,
    upcoming_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all appointments for a specific patient"""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    query = db.query(Appointment).filter(Appointment.patient_id == patient_id)

    # Filter by status if provided
    if status:
        query = query.filter(Appointment.appointment_status == status)

    # Filter to upcoming appointments only
    if upcoming_only:
        now = datetime.now(timezone.utc)
        query = query.filter(
            and_(
                Appointment.appointment_date_time >= now,
                Appointment.appointment_status == "scheduled"
            )
        )

    # Order by appointment date/time
    query = query.order_by(Appointment.appointment_date_time.asc())

    appointments = query.all()
    return appointments


@router.get("/appointments/next/upcoming", response_model=Optional[AppointmentResponse])
def get_next_upcoming_appointment(
    patient_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get the next upcoming appointment (optionally for a specific patient)"""
    now = datetime.now(timezone.utc)

    query = db.query(Appointment).filter(
        and_(
            Appointment.appointment_date_time >= now,
            Appointment.appointment_status == "scheduled"
        )
    )

    # Filter by patient if provided
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)

    # Get the earliest upcoming appointment
    appointment = query.order_by(Appointment.appointment_date_time.asc()).first()

    return appointment


@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: str,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing appointment"""
    appointment = db.query(Appointment).filter(
        Appointment.appointment_id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Update only provided fields
    update_data = appointment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)

    return appointment


@router.delete("/appointments/{appointment_id}", status_code=204)
def delete_appointment(
    appointment_id: str,
    db: Session = Depends(get_db)
):
    """Delete an appointment"""
    appointment = db.query(Appointment).filter(
        Appointment.appointment_id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()

    return None

