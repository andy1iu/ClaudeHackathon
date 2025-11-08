from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.patient import Patient, EHRHistory, ClinicalBriefing
from app.schemas.patient import SynthesizeRequest, ClinicalBriefingResponse
from app.core.config import settings
from anthropic import Anthropic
import json
from datetime import datetime
import uuid

router = APIRouter()


def build_synthesis_prompt(patient: Patient, ehr: EHRHistory, narrative: str) -> str:
    """Build the detailed prompt for Claude API"""

    # Calculate age
    today = datetime.now().date()
    age = today.year - patient.date_of_birth.year - (
        (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
    )

    # Format problem list
    problems = "\n".join([f"- {p['condition']} (ICD-10: {p['icd10']})" for p in ehr.problem_list])

    # Format medications (handle both old string format and new dict format)
    if ehr.medication_list and isinstance(ehr.medication_list[0], dict):
        medications = "\n".join([f"- {m['name']} {m.get('dosage', '')}" for m in ehr.medication_list])
    else:
        medications = "\n".join([f"- {med}" for med in ehr.medication_list])

    # Format recent labs
    labs = "\n".join([f"- {lab['test']}: {lab['value']} (Date: {lab['date']})" for lab in ehr.recent_labs])

    prompt = f"""You are an AI clinical assistant helping to synthesize patient information before a clinical appointment.

You will receive:
1. Patient demographic information
2. Electronic Health Record (EHR) data including problem list, medications, and recent lab results
3. A patient's narrative describing their current concerns in their own words

Your task is to create a structured clinical briefing that will help the clinician quickly understand the patient's situation.

## PATIENT INFORMATION:
Name: {patient.full_name}
Age: {age} years old
Gender Identity: {patient.gender_identity}
Race: {patient.race}

## ELECTRONIC HEALTH RECORD:

### Problem List:
{problems}

### Current Medications:
{medications}

### Recent Lab Results:
{labs if labs else "No recent labs on file"}

## PATIENT NARRATIVE (in their own words):
"{narrative}"

## YOUR TASK:

Please analyze all the information above and create a clinical briefing with the following structure. Respond ONLY with valid JSON in this exact format:

{{
  "ai_summary": "A concise 2-3 sentence clinical summary that synthesizes the patient's chief complaints with their medical history. Focus on the clinical significance and potential connections.",

  "key_insights_flags": [
    {{
      "type": "Risk" or "Opportunity" or "Alert",
      "flag": "Brief title of the insight",
      "reasoning": "Detailed explanation of why this is clinically significant, including specific evidence from the data"
    }}
  ],

  "reported_symptoms_structured": [
    {{
      "symptom": "The symptom name",
      "quality": "Description of how the symptom presents (optional)",
      "location": "Where the symptom occurs (optional)",
      "timing": "When the symptom occurs (optional)"
    }}
  ],

  "relevant_history_surfaced": [
    "List of specific items from the EHR that are directly relevant to understanding or treating the current presentation. Include specific values and dates."
  ]
}}

IMPORTANT GUIDELINES:
- Be thorough but concise
- Identify potential clinical connections between the narrative and the EHR data
- Flag any concerning patterns (e.g., worsening chronic conditions, medication adherence issues, new symptoms suggesting complications)
- Structure symptoms in a way that would be useful for clinical documentation
- Only include EHR history items that are relevant to the current presentation
- Respond with ONLY the JSON object, no additional text or formatting
"""

    return prompt


@router.post("/synthesize", response_model=ClinicalBriefingResponse, status_code=201)
def synthesize_clinical_briefing(
    request: SynthesizeRequest,
    db: Session = Depends(get_db)
):
    """Generate a clinical briefing using Claude AI"""

    # 1. Fetch patient data
    patient = db.query(Patient).filter(Patient.patient_id == request.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 2. Fetch EHR history
    ehr = db.query(EHRHistory).filter(EHRHistory.patient_id == request.patient_id).first()
    if not ehr:
        raise HTTPException(status_code=404, detail="EHR history not found for patient")

    # 3. Build the prompt
    prompt = build_synthesis_prompt(patient, ehr, request.narrative)

    # 4. Call Claude API
    try:
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract the response
        response_text = message.content[0].text

        # Parse the JSON response
        briefing_data = json.loads(response_text)

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse AI response as JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI synthesis failed: {str(e)}"
        )

    # 5. Create and save the briefing
    briefing_id = f"BRIEF-{uuid.uuid4().hex[:10].upper()}"

    new_briefing = ClinicalBriefing(
        briefing_id=briefing_id,
        patient_id=request.patient_id,
        created_at=datetime.utcnow(),
        ai_summary=briefing_data["ai_summary"],
        key_insights_flags=briefing_data["key_insights_flags"],
        reported_symptoms_structured=briefing_data["reported_symptoms_structured"],
        relevant_history_surfaced=briefing_data["relevant_history_surfaced"]
    )

    db.add(new_briefing)
    db.commit()
    db.refresh(new_briefing)

    return new_briefing
