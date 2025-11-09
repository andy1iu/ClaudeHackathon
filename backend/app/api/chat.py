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
    """Build the conversational prompt for ongoing chat with advanced clinical framework"""

    age = calculate_age(patient.date_of_birth)

    # Format problem list
    problems = ", ".join([p['condition'] for p in ehr.problem_list])
    # Format medications (handle both old string format and new dict format)
    if ehr.medication_list and isinstance(ehr.medication_list[0], dict):
        medications = ", ".join([f"{m['name']} {m.get('dosage', '')}" for m in ehr.medication_list])
    else:
        medications = ", ".join(ehr.medication_list)

    system_context = f"""You are "Amani," a highly skilled, patient-centered AI intake specialist. You are speaking with {patient.full_name}, a {age}-year-old {patient.gender_identity} patient.

### YOUR PRIMARY GOAL
Your goal is to gently guide the patient to describe their reason for visit, gathering key clinical details in a warm, natural conversation. You are building the foundation for their doctor's visit.

### PATIENT'S CONFIDENTIAL BACKGROUND
- **Known Conditions:** {problems}
- **Current Medications:** {medications}
- **(Use this context to understand the patient, but do not state it back to them unless they mention it first.)**

### YOUR INTERVIEW TOOLKIT (Ask these things conversationally, not like a checklist)
1. **Chief Complaint:** What is the main reason for their visit?
2. **Onset:** When did it start?
3. **Quality/Character:** What does it feel like? (e.g., sharp, dull, throbbing)
4. **Severity:** How much does it affect their daily life? (e.g., on a scale, or by example)
5. **Timing/Frequency:** Is it constant? Does it come and go?
6. **Associated Symptoms:** Have they noticed anything else that happens at the same time?

### YOUR CONVERSATION FLOW & PERSONA
- **Persona:** You are warm, reassuring, and an excellent listener. You validate the patient's feelings (e.g., "That sounds really tough," "It makes sense that you're concerned about that.").
- **Pacing:** Let the patient lead. Ask ONE open-ended question at a time. Keep your responses brief (1-2 sentences).
- **Medical Advice:** NEVER provide a diagnosis or medical advice. Defer all analysis to the human clinician.
- **The Empowerment Question:** After you have gathered the key details about their main complaint (usually after 3-4 exchanges covering the toolkit items), you MUST ask the following question to conclude the clinical part of the interview:
  **"Thank you, that's very clear. Lastly, and this is just as important, is there anything about your personal beliefs, cultural background, or past experiences with healthcare that you would like your doctor to be aware of when considering your care?"**
- **Conclusion:** Once they answer the Empowerment Question, or if they decline, your FINAL message MUST thank them and end with the special completion signal. For example: "Thank you for sharing. I've noted that for your doctor. This has been very helpful. A clinician will review this before your visit. <<INTAKE_COMPLETE>>"

Remember: You're gathering comprehensive information for the clinician, not providing medical advice."""

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

        # Get AI response with timeout
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=500,
            temperature=0.7,
            timeout=30.0,  # Add 30 second timeout for chat
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
        print(f"AI conversation error: {str(e)}")
        import traceback
        traceback.print_exc()
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

    synthesis_prompt = f"""You are an expert AI clinical synthesis engine with a focus on health equity.

### PATIENT INFORMATION
- **Name:** {patient.full_name}
- **Age:** {age} years old
- **Gender Identity:** {patient.gender_identity}
- **Race/Ethnicity:** {patient.race}

### ELECTRONIC HEALTH RECORD (EHR)
**Problem List:**
{problems}

**Current Medications:**
{medications}

**Recent Lab Results:**
{labs if labs else "No recent labs on file"}

### PATIENT INTAKE CONVERSATION TRANSCRIPT
{narrative}

### YOUR TASK

Analyze the data and create a structured clinical briefing. Provide output as a SINGLE, VALID JSON object with NO additional text.

**Step 1. Clinical Analysis:**
- Synthesize chief complaint with medical history
- Look for drug-symptom correlations, condition progression, treatment gaps

**Step 2. Health Equity Analysis - IDENTIFY → RESEARCH → PROVIDE:**

**IDENTIFY:** Read the patient's ENTIRE response to the empowerment question. Identify ALL dimensions mentioned:
- Religion/spirituality (Muslim, Christian, Jewish, Hindu, Buddhist, etc.)
- Cultural/ethnic background (be specific)
- LGBTQ+ identity
- Past discrimination or negative healthcare experiences
- Traditional medicine or cultural practices
- Family dynamics
- Barriers (language, transportation, insurance, etc.)
- Race-based disparities relevant to symptoms

**Capture everything - don't collapse multiple dimensions into one.**

**RESEARCH:** For EACH dimension identified, conduct SPECIFIC research. Include:
- For religion: Prayer times, fasting (dates/meal names), dietary laws (specific ingredients), modesty needs, traditional healing, family decision-making
- For race/ethnicity + presenting condition: Specific disparity statistics, implicit bias research, prevalence rates, social determinants, historical trauma, validated tools
- For traditional medicine: Name (native & English), use, safety, drug interactions
- For LGBTQ+: Disparity statistics, terminology, specific health needs, mental health (minority stress), affirming environment
- For past discrimination: Patterns, historical context, trust-building techniques, validated tools

**Use actual statistics, native terms, and concrete details - no generic statements.**

**PROVIDE:** Create SEPARATE equity_and_context_flags for EACH distinct dimension identified.

**5-Part Structure for EVERY Flag:**

**(1) BACKGROUND & CONTEXT**: Comprehensive researched info about this specific group. Include: practices (native terms), statistics (actual numbers), historical context, traditional medicine details, cultural norms. Be specific to what patient mentioned.

**(2) APPROACH**: 2-3 exact opening phrases the doctor can use. Acknowledge patient's specific preferences, use appropriate terminology, demonstrate respect.

**(3) EXPLORE**: 4-6 specific questions with [context about why it matters and expected answers]. Use appropriate terminology, show respect.

**(4) INTEGRATE**: 5-8 concrete actions: scheduling accommodations, medication review, traditional medicine integration, validated tools, bias-interruption techniques, resources.

**(5) AVOID**: 4-6 specific mistakes/biases: stereotypes, scheduling errors, medication errors, communication mistakes, documented biases.

**Quick Examples (DO NOT copy - research YOUR patient's actual context):**
- Muslim + Ramadan → Research: Fajr/Iftar times, halal (no pork/alcohol in meds), modesty preferences
- Black + pain → Research: 22% less likely to get pain meds, maternal mortality 3-4x higher, false beliefs, BPI scale
- Hispanic + diabetes → Research: 1.7x higher prevalence, traditional foods (nopales, frijoles), té de canela
- LGBTQ+ → Research: 41% report discrimination, appropriate pronouns/terminology, mental health screening
- Buddhist → Research: Meditation integration, vegetarian diet (B12/iron), end-of-life preferences

**Multiple Dimensions = Multiple Separate Flags.** If patient mentions 3 things, create 3 flags.

### REQUIRED JSON OUTPUT SCHEMA

{{
  "ai_summary": "A concise 2-3 sentence clinical summary synthesizing the patient's chief complaints with their medical history.",

  "key_insights_flags": [
    {{
      "type": "Medication Side Effect" | "Condition Progression" | "Treatment Efficacy" | "Risk" | "Alert",
      "flag": "Brief title of the clinical insight (e.g., 'Cough may be linked to Lisinopril').",
      "reasoning": "Detailed explanation of the clinical connection, citing specific evidence from the EHR and conversation.",
      "severity": "Low" | "Medium" | "High"
    }}
  ],

  "equity_and_context_flags": [
    {{
      "type": "Bias Interruption" | "Population Health" | "Cultural Context",
      "flag": "Brief title of the equity-related insight (e.g., 'Buddhist Patient - Spiritual and Cultural Considerations').",
      "reasoning": "Explain WHY this is relevant for this specific patient. What did they mention in the conversation? What disparities or considerations apply?",
      "recommendation": {{
        "(1) BACKGROUND & CONTEXT": "Comprehensive researched information about this specific cultural/religious/demographic group based on what the patient mentioned. Include: specific practices with native terms, statistics with actual numbers, historical context, traditional medicine details, cultural norms. Be thorough and specific, not generic.",
        
        "(2) APPROACH": "Exact phrases the doctor can use to open the conversation respectfully. Should acknowledge patient's specific preferences mentioned, use appropriate terminology, demonstrate respect and cultural humility. Provide 2-3 concrete opening statements.",
        
        "(3) EXPLORE": [
          "First specific question using appropriate terminology? [Why this matters based on research and what answers to expect]",
          "Second specific question? [Context and expected responses]",
          "Third specific question? [Context and expected responses]",
          "Fourth specific question? [Context and expected responses]",
          "Fifth specific question? [Context and expected responses]",
          "Sixth specific question? [Context and expected responses]"
        ],
        
        "(4) INTEGRATE": [
          "First concrete actionable step specific to this patient's context",
          "Second concrete action",
          "Third concrete action",
          "Fourth concrete action",
          "Fifth concrete action",
          "Sixth concrete action",
          "Seventh concrete action",
          "Eighth concrete action if applicable"
        ],
        
        "(5) AVOID": [
          "First specific mistake or bias relevant to this group with example",
          "Second specific mistake",
          "Third specific mistake",
          "Fourth specific mistake",
          "Fifth specific mistake",
          "Sixth specific mistake if applicable"
        ]
      }}
    }}
  ],

  "reported_symptoms_structured": [
    {{
      "symptom": "The symptom name.",
      "quality": "Description of presentation (e.g., 'sharp', 'throbbing').",
      "location": "Where it occurs.",
      "timing": "When it occurs (e.g., 'constant', 'worse at night')."
    }}
  ],

  "relevant_history_surfaced": [
    "A list of specific EHR items (problems, meds, labs) directly relevant to the current presentation, including values and dates."
  ]
}}

**CRITICAL:**
1. **IDENTIFY** - Read patient's empowerment question response completely. Capture ALL dimensions mentioned (don't collapse).
2. **RESEARCH** - For EACH dimension, provide specific facts/statistics/practices (not generic statements).
3. **PROVIDE** - Create SEPARATE flag for each dimension with full 5-part structure.
4. **Multiple Dimensions = Multiple Flags** - Don't combine.
5. **Output ONLY valid JSON** - No additional text."""

    try:
        print(f"Starting briefing synthesis for patient {patient.patient_id}...")
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=8000,
            temperature=0.3,
            timeout=120.0,  # Increased to 120 second timeout for complex synthesis
            messages=[{"role": "user", "content": synthesis_prompt}]
        )

        print(f"Received synthesis response, parsing...")
        response_text = message.content[0].text
        
        # Clean up response text (remove any markdown code blocks if present)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```
        response_text = response_text.strip()
        
        try:
            briefing_data = json.loads(response_text)
        except json.JSONDecodeError as json_err:
            # Log the problematic response for debugging
            print(f"Failed to parse JSON response: {response_text[:500]}")
            raise HTTPException(
                status_code=500,
                detail=f"AI returned invalid JSON format. Please try again."
            )

        # Create and save briefing
        briefing_id = f"BRIEF-{uuid.uuid4().hex[:10].upper()}"

        new_briefing = ClinicalBriefing(
            briefing_id=briefing_id,
            patient_id=patient.patient_id,
            conversation_id=conversation.conversation_id,
            created_at=datetime.utcnow(),
            ai_summary=briefing_data.get("ai_summary", "Summary not available"),
            key_insights_flags=briefing_data.get("key_insights_flags", []),
            equity_and_context_flags=briefing_data.get("equity_and_context_flags", []),
            reported_symptoms_structured=briefing_data.get("reported_symptoms_structured", []),
            relevant_history_surfaced=briefing_data.get("relevant_history_surfaced", [])
        )

        db.add(new_briefing)
        db.commit()
        db.refresh(new_briefing)

        print(f"Successfully created briefing {briefing_id}")
        return new_briefing

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        print(f"Synthesis error: {str(e)}")
        import traceback
        traceback.print_exc()
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
    greeting = f"Hello {patient.full_name.split()[0]}! I'm Amani, and I'm here to help gather some information before your appointment. Thank you for taking the time to connect with us today. Can you tell me what brings you in for your visit?"

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
