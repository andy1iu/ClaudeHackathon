from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import date, datetime


class ProblemItem(BaseModel):
    condition: str
    icd10: str
    date_diagnosed: Optional[str] = None


class MedicationItem(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None


class LabResult(BaseModel):
    test: str
    value: str
    date: str
    unit: Optional[str] = None


class SurgicalHistoryItem(BaseModel):
    year: int
    procedure: str
    indication: Optional[str] = None


class AllergyItem(BaseModel):
    allergen: str
    reaction: str
    severity: Optional[str] = None


class SocialHistory(BaseModel):
    alcohol: Optional[str] = None
    tobacco: Optional[str] = None
    occupation: Optional[str] = None
    living_situation: Optional[str] = None


class FamilyHistoryItem(BaseModel):
    relation: str
    age: Optional[str] = None  # Can be int or "deceased"
    conditions: List[str]
    age_at_death: Optional[int] = None
    cause_of_death: Optional[str] = None


class VitalSigns(BaseModel):
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    temperature: Optional[float] = None
    date: Optional[str] = None


class EHRHistoryBase(BaseModel):
    problem_list: List[ProblemItem]
    medication_list: List[MedicationItem]
    recent_labs: List[LabResult]
    surgical_history: Optional[List[SurgicalHistoryItem]] = None
    allergies: Optional[List[AllergyItem]] = None
    social_history: Optional[SocialHistory] = None
    family_history: Optional[List[FamilyHistoryItem]] = None
    vital_signs: Optional[VitalSigns] = None


class PatientBase(BaseModel):
    patient_id: str
    full_name: str
    date_of_birth: date
    gender_identity: str
    race: str
    address_zip_code: str


class PatientResponse(PatientBase):
    briefing_status: str  # "Pending Intake" or "Briefing Ready"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientNarrativeBase(BaseModel):
    narrative_id: str
    patient_id: str
    narrative_title: str
    narrative_text: str


class PatientNarrativeResponse(PatientNarrativeBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KeyInsightFlag(BaseModel):
    type: str
    flag: str
    reasoning: str
    severity: Optional[str] = None  # "Low" | "Medium" | "High"


class RecommendationDetail(BaseModel):
    background_context: Optional[str] = None
    approach: Optional[str] = None
    explore_questions: Optional[List[str]] = None
    integrate_actions: Optional[List[str]] = None
    avoid: Optional[List[str]] = None


class EquityContextFlag(BaseModel):
    type: str  # "Bias Interruption" | "Population Health" | "Cultural Context"
    flag: str
    reasoning: str
    recommendation: Optional[Union[str, RecommendationDetail]] = None


class ReportedSymptom(BaseModel):
    symptom: str
    quality: Optional[str] = None
    location: Optional[str] = None
    timing: Optional[str] = None


class ClinicalBriefingBase(BaseModel):
    briefing_id: str
    patient_id: str
    created_at: datetime
    updated_at: datetime
    ai_summary: str
    key_insights_flags: List[KeyInsightFlag]
    equity_and_context_flags: Optional[List[EquityContextFlag]] = None
    reported_symptoms_structured: List[ReportedSymptom]
    relevant_history_surfaced: List[str]


class ClinicalBriefingResponse(ClinicalBriefingBase):
    class Config:
        from_attributes = True


class SynthesizeRequest(BaseModel):
    patient_id: str
    narrative: str


class ChatMessage(BaseModel):
    role: str  # "ai" or "user"
    content: str


class ChatStartRequest(BaseModel):
    patient_id: str


class ChatStartResponse(BaseModel):
    conversation_id: str
    patient_id: str
    initial_message: ChatMessage
    is_complete: bool = False


class ChatContinueRequest(BaseModel):
    conversation_id: str
    user_message: str


class ChatContinueResponse(BaseModel):
    conversation_id: str
    ai_message: ChatMessage
    is_complete: bool
    briefing_id: Optional[str] = None  # Populated when conversation completes
    thinking: Optional[List[str]] = None  # Real-time thinking steps from Claude


class AppointmentBase(BaseModel):
    appointment_id: str
    patient_id: str
    appointment_date_time: datetime
    appointment_status: str  # scheduled, completed, cancelled, no_show, rescheduled
    appointment_type: Optional[str] = None  # initial, follow_up, consultation, urgent, routine
    duration_minutes: Optional[int] = 30
    location: Optional[str] = None  # in_person, virtual, phone
    provider_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AppointmentCreate(BaseModel):
    patient_id: str
    appointment_date_time: datetime
    appointment_type: Optional[str] = None
    duration_minutes: Optional[int] = 30
    location: Optional[str] = None
    provider_name: Optional[str] = None
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    appointment_date_time: Optional[datetime] = None
    appointment_status: Optional[str] = None
    appointment_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    provider_name: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    class Config:
        from_attributes = True
