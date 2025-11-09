from sqlalchemy import Column, String, Date, JSON, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender_identity = Column(String, nullable=False)
    race = Column(String, nullable=False)
    address_zip_code = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)

    # Relationships
    ehr_history = relationship("EHRHistory", back_populates="patient", uselist=False)
    narratives = relationship("PatientNarrative", back_populates="patient")
    briefings = relationship("ClinicalBriefing", back_populates="patient")
    conversations = relationship("ChatConversation", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")


class EHRHistory(Base):
    __tablename__ = "ehr_histories"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)

    # Medical History
    problem_list = Column(JSON, nullable=False)  # [{"condition": str, "icd10": str, "date_diagnosed": str}]
    medication_list = Column(JSON, nullable=False)  # [{"name": str, "dosage": str, "frequency": str}]
    recent_labs = Column(JSON, nullable=False)  # [{"test": str, "value": str, "date": str, "unit": str}]

    # Surgical History
    surgical_history = Column(JSON, nullable=True)  # [{"year": int, "procedure": str, "indication": str}]

    # Allergy Information
    allergies = Column(JSON, nullable=True)  # [{"allergen": str, "reaction": str, "severity": str}]

    # Social History
    social_history = Column(JSON, nullable=True)  # {"alcohol": str, "tobacco": str, "occupation": str, "living_situation": str}

    # Family History
    family_history = Column(JSON, nullable=True)  # [{"relation": str, "age": int/str, "conditions": [str], "age_at_death": int/None, "cause_of_death": str/None}]

    # Vital Signs (most recent)
    vital_signs = Column(JSON, nullable=True)  # {"bp_systolic": int, "bp_diastolic": int, "heart_rate": int, "respiratory_rate": int, "temperature": float, "date": str}

    # Relationship
    patient = relationship("Patient", back_populates="ehr_history")


class PatientNarrative(Base):
    __tablename__ = "patient_narratives"

    narrative_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False)
    narrative_title = Column(String, nullable=False)
    narrative_text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)

    # Relationship
    patient = relationship("Patient", back_populates="narratives")


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    conversation_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)
    is_complete = Column(Boolean, default=False, nullable=False)
    messages = Column(JSON, nullable=False, default=list)  # Array of {role, content} objects

    # Relationships
    patient = relationship("Patient", back_populates="conversations")
    briefing = relationship("ClinicalBriefing", back_populates="conversation", uselist=False)


class ClinicalBriefing(Base):
    __tablename__ = "briefings"

    briefing_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False)
    conversation_id = Column(String, ForeignKey("chat_conversations.conversation_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)
    ai_summary = Column(String, nullable=False)
    key_insights_flags = Column(JSON, nullable=False)
    equity_and_context_flags = Column(JSON, nullable=True)  # New field for health equity insights
    reported_symptoms_structured = Column(JSON, nullable=False)
    relevant_history_surfaced = Column(JSON, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="briefings")
    conversation = relationship("ChatConversation", back_populates="briefing")


class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    appointment_date_time = Column(DateTime(timezone=True), nullable=False, index=True)
    appointment_status = Column(String, nullable=False, default="scheduled", index=True)  # scheduled, completed, cancelled, no_show, rescheduled
    appointment_type = Column(String, nullable=True)  # initial, follow_up, consultation, urgent, routine
    duration_minutes = Column(Integer, nullable=True, default=30)  # Default 30 minutes
    location = Column(String, nullable=True)  # in_person, virtual, phone
    provider_name = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
