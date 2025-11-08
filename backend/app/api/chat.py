from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.patient import Patient, EHRHistory, ChatConversation, ClinicalBriefing
from app.schemas.patient import (
    ChatStartRequest, ChatStartResponse, ChatContinueRequest,
    ChatContinueResponse, ChatMessage
)
from app.core.config import settings
from anthropic import Anthropic
import json
from datetime import datetime
import uuid

router = APIRouter()


def calculate_age(date_of_birth):
    """Calculate age from date of birth"""
    today = datetime.now().date()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def build_conversational_prompt(patient: Patient, ehr: EHRHistory, messages: list) -> str:
    """Build the conversational prompt for ongoing chat"""

    age = calculate_age(patient.date_of_birth)

    # Format problem list
    problems = ", ".join([p['condition'] for p in ehr.problem_list])
    # Format medications (handle both old string format and new dict format)
    if ehr.medication_list and isinstance(ehr.medication_list[0], dict):
        medications = ", ".join([f"{m['name']} {m.get('dosage', '')}" for m in ehr.medication_list])
    else:
        medications = ", ".join(ehr.medication_list)

    system_context = f"""You are an empathetic AI medical intake assistant conducting a pre-visit interview with {patient.full_name}, a {age}-year-old {patient.gender_identity} patient.

PATIENT CONTEXT (Keep this confidential, don't reveal unless necessary):
- Known conditions: {problems}
- Current medications: {medications}

YOUR ROLE:
- Conduct a warm, empathetic conversation to understand why they're seeking care today
- Ask open-ended follow-up questions to gather clinical details
- Listen for symptoms, concerns, and how they're affecting daily life
- Be conversational and supportive, not robotic
- Keep responses brief and natural (2-3 sentences max per turn)
- After 3-4 meaningful exchanges, conclude the conversation gracefully

CONVERSATION COMPLETION:
- When you have enough information about their chief complaint and relevant details, your LAST message should thank them and let them know a clinician will review this information
- Signal completion by ending with exactly: "<<INTAKE_COMPLETE>>"

Remember: You're gathering information for the clinician, not providing medical advice."""

    return system_context


def get_ai_response(patient: Patient, ehr: EHRHistory, messages: list) -> tuple[str, bool]:
    """Get AI response and determine if conversation is complete"""

    try:
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Build the conversation context
        system_prompt = build_conversational_prompt(patient, ehr, messages)

        # Format messages for Claude API
        api_messages = []
        for msg in messages:
            api_messages.append({
                "role": "assistant" if msg["role"] == "ai" else "user",
                "content": msg["content"]
            })

        # Get AI response
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=500,
            temperature=0.7,
            system=system_prompt,
            messages=api_messages
        )

        ai_message = response.content[0].text

        # Check if conversation is complete
        is_complete = "<<INTAKE_COMPLETE>>" in ai_message

        # Remove the completion marker from the message
        ai_message = ai_message.replace("<<INTAKE_COMPLETE>>", "").strip()

        return ai_message, is_complete

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI conversation failed: {str(e)}"
        )


def synthesize_from_conversation(
    db: Session,
    patient: Patient,
    ehr: EHRHistory,
    conversation: ChatConversation
) -> ClinicalBriefing:
    """Synthesize clinical briefing from completed conversation"""

    # Build narrative from conversation
    narrative_parts = []
    for msg in conversation.messages:
        if msg["role"] == "user":
            narrative_parts.append(msg["content"])

    narrative = "\n\n".join(narrative_parts)

    age = calculate_age(patient.date_of_birth)

    # Format EHR data
    problems = "\n".join([f"- {p['condition']} (ICD-10: {p['icd10']})" for p in ehr.problem_list])
    # Format medications (handle both old string format and new dict format)
    if ehr.medication_list and isinstance(ehr.medication_list[0], dict):
        medications = "\n".join([f"- {m['name']} {m.get('dosage', '')}" for m in ehr.medication_list])
    else:
        medications = "\n".join([f"- {med}" for med in ehr.medication_list])
    labs = "\n".join([f"- {lab['test']}: {lab['value']} (Date: {lab['date']})" for lab in ehr.recent_labs])

    synthesis_prompt = f"""You are an AI clinical assistant creating a structured briefing from a patient intake conversation.

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

## PATIENT INTAKE CONVERSATION:
{narrative}

## YOUR TASK:

Analyze the conversation and EHR data to create a clinical briefing. Respond ONLY with valid JSON in this exact format:

{{
  "ai_summary": "A concise 2-3 sentence clinical summary synthesizing the patient's chief complaints with their medical history. Focus on clinical significance and potential connections.",

  "key_insights_flags": [
    {{
      "type": "Risk" or "Opportunity" or "Alert",
      "flag": "Brief title of the insight",
      "reasoning": "Detailed explanation of clinical significance with specific evidence"
    }}
  ],

  "reported_symptoms_structured": [
    {{
      "symptom": "The symptom name",
      "quality": "Description of presentation (optional)",
      "location": "Where it occurs (optional)",
      "timing": "When it occurs (optional)"
    }}
  ],

  "relevant_history_surfaced": [
    "Specific EHR items directly relevant to current presentation with values and dates"
  ]
}}

IMPORTANT:
- Be thorough but concise
- Identify clinical connections between conversation and EHR
- Flag concerning patterns (worsening conditions, adherence issues, complications)
- Structure symptoms for clinical documentation
- Only include relevant EHR history items
- Respond with ONLY the JSON object"""

    try:
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": synthesis_prompt}]
        )

        response_text = message.content[0].text
        briefing_data = json.loads(response_text)

        # Create and save briefing
        briefing_id = f"BRIEF-{uuid.uuid4().hex[:10].upper()}"

        new_briefing = ClinicalBriefing(
            briefing_id=briefing_id,
            patient_id=patient.patient_id,
            conversation_id=conversation.conversation_id,
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

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse synthesis response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Synthesis failed: {str(e)}"
        )


@router.post("/chat/start", response_model=ChatStartResponse, status_code=201)
def start_chat(
    request: ChatStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new patient intake chat conversation"""

    # Fetch patient
    patient = db.query(Patient).filter(Patient.patient_id == request.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Fetch EHR
    ehr = db.query(EHRHistory).filter(EHRHistory.patient_id == request.patient_id).first()
    if not ehr:
        raise HTTPException(status_code=404, detail="EHR history not found")

    # Create conversation ID
    conversation_id = f"CONVO-{uuid.uuid4().hex[:10].upper()}"

    # Generate initial greeting
    age = calculate_age(patient.date_of_birth)
    greeting = f"Hello {patient.full_name.split()[0]}! Thank you for connecting with us today. I'm here to help gather some information before your appointment. Can you tell me what brings you in today?"

    # Create initial messages
    initial_messages = [
        {"role": "ai", "content": greeting}
    ]

    # Save conversation
    conversation = ChatConversation(
        conversation_id=conversation_id,
        patient_id=request.patient_id,
        created_at=datetime.utcnow(),
        is_complete=False,
        messages=initial_messages
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return ChatStartResponse(
        conversation_id=conversation_id,
        patient_id=request.patient_id,
        initial_message=ChatMessage(role="ai", content=greeting),
        is_complete=False
    )


@router.post("/chat/continue", response_model=ChatContinueResponse)
def continue_chat(
    request: ChatContinueRequest,
    db: Session = Depends(get_db)
):
    """Continue an existing chat conversation"""

    # Fetch conversation
    conversation = db.query(ChatConversation).filter(
        ChatConversation.conversation_id == request.conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.is_complete:
        raise HTTPException(status_code=400, detail="Conversation already complete")

    # Fetch patient and EHR
    patient = db.query(Patient).filter(Patient.patient_id == conversation.patient_id).first()
    ehr = db.query(EHRHistory).filter(EHRHistory.patient_id == conversation.patient_id).first()

    # Add user message to conversation
    messages = conversation.messages.copy() if conversation.messages else []
    messages.append({
        "role": "user",
        "content": request.user_message
    })

    # Get AI response
    ai_message, is_complete = get_ai_response(patient, ehr, messages)

    # Add AI response to conversation
    messages.append({
        "role": "ai",
        "content": ai_message
    })

    # Update conversation with new messages array
    conversation.messages = messages
    conversation.is_complete = is_complete

    # Mark the messages column as modified for SQLAlchemy to detect the change
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(conversation, "messages")

    db.commit()
    db.refresh(conversation)

    # If conversation is complete, trigger synthesis
    briefing_id = None
    if is_complete:
        briefing = synthesize_from_conversation(db, patient, ehr, conversation)
        briefing_id = briefing.briefing_id

    return ChatContinueResponse(
        conversation_id=conversation.conversation_id,
        ai_message=ChatMessage(role="ai", content=ai_message),
        is_complete=is_complete,
        briefing_id=briefing_id
    )
