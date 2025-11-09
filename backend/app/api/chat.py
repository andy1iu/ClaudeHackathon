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

    synthesis_prompt = f"""You are an expert AI clinical synthesis engine with a focus on health equity. Your task is to analyze the following patient data and produce a structured, insightful clinical briefing for a doctor.

### CRITICAL GUIDING PRINCIPLES
1. **Context, Not Causation:** Patient race and ethnicity are social constructs, not biological determinants. Use this information ONLY to consider potential risks of systemic bias, social determinants of health (SDOH), and population-level health disparities from trusted sources.
2. **Augment, Don't Diagnose:** Your role is to surface potential connections and risks to augment the clinician's judgment. You are not making a diagnosis.
3. **Evidence-Based:** Every insight you flag must be directly supported by the data provided (EHR or conversation).

### PATIENT INFORMATION
- **Name:** {patient.full_name}
- **Age:** {age} years old
- **Gender Identity:** {patient.gender_identity}
- **Race/Ethnicity:** {patient.race}

### ELECTRONIC HEALTH RECORD (EHR)

#### Problem List:
{problems}

#### Current Medications:
{medications}

#### Recent Lab Results:
{labs if labs else "No recent labs on file"}

### PATIENT INTAKE CONVERSATION TRANSCRIPT
{narrative}

### YOUR ANALYSIS FRAMEWORK & OUTPUT

Follow these steps in your reasoning, then provide the output as a SINGLE, VALID JSON object with NO additional text or explanations.

**Step 1. Synthesize the Chief Complaint:** Create a concise clinical summary.

**Step 2. Deep Clinical Analysis:** Cross-reference the conversation with the EHR. Look for:
- **Drug-Symptom Correlations:** Could a reported symptom be a known side effect of a current medication?
- **Condition Progression:** Do the symptoms suggest a worsening of a known chronic condition?
- **Treatment Gaps:** Is the patient reporting issues that suggest their current treatment is not fully effective?

**Step 3. Health Equity Analysis:** Based on the patient's race/ethnicity, gender, and narrative, proactively consider known health disparities and inequities.

**CRITICAL: Create SEPARATE equity_and_context_flags for EACH distinct dimension of patient identity/context that was mentioned:**
- If patient mentions religious/spiritual identity → CREATE A FLAG for that
- If patient mentions sexual orientation/gender identity → CREATE A SEPARATE FLAG for that  
- If patient mentions past discrimination → CREATE A FLAG for that
- If patient mentions cultural practices → CREATE A FLAG for that
- If patient's race/ethnicity has documented disparities relevant to their presenting symptoms → CREATE A FLAG for that

**DO NOT collapse multiple identity dimensions into a single flag.** Each significant aspect deserves its own detailed analysis and recommendations.

Consider these dimensions independently:

- **Race-Based Health Disparities:** What are documented health inequities for this patient's demographic? Examples:
  - Black patients: Pain undertreatment (22% less likely to receive pain medication), maternal mortality (3-4x higher than white women), cardiovascular disease disparities, higher rates of certain cancers
  - Hispanic/Latino patients: Diabetes (1.7x higher prevalence), cardiovascular disease, lower screening rates for certain cancers
  - Asian American patients: Mental health stigma, lower mental health service utilization, higher rates of certain cancers (liver, stomach)
  - Indigenous populations: Highest rates of diabetes, substance use disorders, maternal mortality
  
- **Intersectionality:** Consider how multiple identities interact. Example: A Black woman with a college degree is STILL more likely to experience severe maternal morbidity than a white woman with an 8th-grade education - showing that race trumps education in healthcare outcomes.

- **Bias Interruption:** Are they reporting symptoms (e.g., pain, fatigue, mental health concerns) that research shows are often dismissed or underestimated in their demographic?

- **Population Health Risks:** Are there conditions with higher prevalence in this demographic that should be proactively screened for?

- **Cultural Context:** Did the patient mention any beliefs, experiences with healthcare discrimination, or cultural practices that the doctor should be aware of?

- **Structural Barriers:** What systemic issues might this patient face? (Insurance access, food deserts, transportation, language barriers, immigration concerns, etc.)

**Step 4. Generate the JSON Output:** Populate the following JSON schema with your findings.

### FRAMEWORK FOR PROVIDING DETAILED, RESEARCHED RECOMMENDATIONS

When creating equity_and_context_flags, follow this research framework. DO NOT use hardcoded examples - dynamically research based on what the patient ACTUALLY shared in the conversation.

**IDENTIFY the specific cultural/religious/ethnic context from the patient's conversation:**
- What religion did they mention? (Muslim, Christian, Jewish, Hindu, Buddhist, etc.)
- What cultural background? (Hispanic/Latino, Asian American specific ethnicity, African/Caribbean, Indigenous, etc.)
- What specific practices or preferences did they mention? (Traditional medicine, dietary needs, language, healthcare experiences)
- What concerns did they express? (Past discrimination, specific symptoms, family preferences)

**THEN provide comprehensive research for THAT specific context:**

(1) BACKGROUND & CONTEXT: Research and provide DETAILED, SPECIFIC information about THIS patient's cultural/religious/ethnic group. Structure your research to include:

   **For Religious/Cultural Context - Provide specifics like:**
   - Religious practices that affect healthcare (prayer times with names and typical times, fasting periods with dates/timing, holy days to avoid scheduling)
   - Dietary laws (specific foods to avoid, why, and how this affects medications/nutrition advice)
   - Medication ingredient restrictions (specific ingredients to check, alternatives to suggest)
   - Modesty/gender considerations (which exams, how to accommodate)
   - Traditional healing practices (names in native language, what they are, safety considerations, drug interactions)
   - Family decision-making norms (individual vs. collective, who is typically involved)

   **For Race/Ethnicity-Based Disparities - Provide specifics like:**
   - Documented health disparities for this demographic (specific statistics, not general statements)
   - Research on bias (cite specific studies, percentages, examples)
   - Higher-prevalence conditions (exact prevalence rates compared to general population)
   - Social determinants affecting this group (food access, language barriers, insurance, immigration)
   - Historical medical trauma relevant to this group

(2) APPROACH: Create a culturally appropriate opening that:
   - Acknowledges their specific preferences mentioned in the conversation
   - Uses appropriate cultural/religious terminology
   - Shows respect and cultural humility
   - Provides exact phrases the doctor can say

(3) EXPLORE: Provide 4-6 specific questions with FULL CONTEXT:
   - Each question should relate to the specific culture/religion/ethnicity identified
   - Include WHY the question matters (in brackets)
   - Include what answers to expect
   - Use culturally appropriate terminology
   - Show respect and openness

(4) INTEGRATE: Provide concrete, specific actions for THIS cultural/religious/ethnic context:
   - Specific scheduling accommodations (if religious practices mentioned)
   - Specific medications to review (if dietary laws mentioned)
   - Specific provider matching (if preferences mentioned)
   - Specific traditional medicine integration (if practices mentioned)
   - Specific bias-interruption actions (if disparity exists)
   - Specific resource connections (language-appropriate, culturally tailored)

(5) AVOID: List specific mistakes/biases relevant to THIS group:
   - Common stereotypes about this group
   - Common scheduling errors (if relevant)
   - Common medication errors (if relevant)
   - Common communication mistakes
   - Documented biases in research about this group

**EXAMPLES OF THE RESEARCH YOU SHOULD PROVIDE:**

If patient mentions Muslim faith:
→ Research Islamic prayer times (names, times), Ramadan fasting (dates, meal names), halal requirements (specific ingredients), hijama/traditional medicine, modesty norms, family involvement

If patient mentions Buddhist practice:
→ Research Buddhist meditation/mindfulness practices, vegetarian dietary preferences, end-of-life considerations, traditional medicine (TCM if relevant), family communication norms

If patient mentions Hispanic ethnicity + diabetes concern:
→ Research diabetes prevalence in Hispanic populations (exact statistics), traditional foods and how to adapt them, common remedies (té de canela, nopal), food access barriers, language resources

If patient mentions past healthcare discrimination as Black patient:
→ Research pain undertreatment statistics, maternal mortality disparities, implicit bias studies, validated assessment tools, specific bias-interruption techniques

**BE COMPREHENSIVE AND SPECIFIC. AVOID GENERIC STATEMENTS. Always tie back to what THIS specific patient mentioned in their conversation.**

### EXAMPLE: HOW TO APPLY THE FRAMEWORK

This shows HOW to apply the framework dynamically based on patient information. DO NOT copy this verbatim - research based on YOUR specific patient's conversation.

**Example Application: If patient is Black female + mentions past dismissal OR presenting with pain/pregnancy concerns:**

Apply framework by researching:
- Maternal mortality statistics for Black women (3-4x higher, persists across education levels)
- Pain undertreatment data (22% less likely to receive pain medication)
- Intersectionality (college-educated Black woman > white woman with 8th-grade education for maternal outcomes)
- Historical context (medical experimentation, false beliefs about pain tolerance)
- Validated tools (BPI, PEG scale, specific pain assessment)
- Bias-interruption techniques (taking believing stance, thorough documentation)

Then structure the recommendation with this researched information, providing specific statistics, concrete actions, and culturally appropriate language.

**Example Application: If patient mentions Hindu faith + vegetarian diet:**

Apply framework by researching:
- Ayurvedic medicine practices (doshas, herbs commonly used, safety)
- Vegetarian nutritional considerations (protein sources, B12, iron)
- Religious fasting practices (specific days, how to adjust medications)
- Meditation/yoga as complementary therapies (evidence base, integration)
- End-of-life care preferences (family involvement, religious rituals)
- Dietary restrictions beyond vegetarian (onion/garlic avoidance in some practices)

**Example Application: If patient mentions Indigenous background + diabetes:**

Apply framework by researching:
- Diabetes prevalence in Indigenous populations (highest rates in U.S.)
- Historical trauma from forced assimilation and impact on health
- Traditional healing practices (smudging, sweat lodge, herbal medicine)
- Barriers to care (IHS underfunding, geographic isolation)
- Cultural values (storytelling, community, traditional foods)
- Distrust of medical system (historical experimentation, forced sterilization)

**The key: IDENTIFY → RESEARCH → PROVIDE SPECIFICS for the actual patient's context. Don't use templates.**

### INTERSECTIONALITY: CREATING MULTIPLE FLAGS FOR MULTIPLE IDENTITIES

**CRITICAL RULE:** When a patient mentions MULTIPLE aspects of their identity (e.g., "I'm Buddhist and I'm gay and had a bad experience"), you MUST create SEPARATE equity_and_context_flags for EACH distinct dimension:

**Example: Patient says "I'm Buddhist and had a bad experience with my doctor because I'm gay"**

This patient mentioned TWO distinct identity dimensions, so create TWO separate flags:

FLAG 1 - Religious/Spiritual Identity:
{{
  "type": "Cultural Context",
  "flag": "Buddhist Patient - Spiritual and Cultural Considerations",
  "reasoning": "Patient identifies as Buddhist, which may involve specific healthcare preferences and practices that should be integrated into care.",
  "recommendation": {{
    "(1) BACKGROUND & CONTEXT": {{ ... research Buddhist practices, meditation, dietary preferences, end-of-life care, traditional medicine ... }},
    "(2) APPROACH": "... culturally sensitive opening about Buddhist practices ...",
    "(3) EXPLORE": [ ... questions about Buddhist practices and preferences ... ],
    "(4) INTEGRATE": [ ... specific actions for Buddhist patients ... ],
    "(5) AVOID": [ ... mistakes to avoid with Buddhist patients ... ]
  }}
}}

FLAG 2 - LGBTQ+ Identity + Healthcare Discrimination:
{{
  "type": "Bias Interruption",
  "flag": "LGBTQ+ Patient with Past Healthcare Discrimination",
  "reasoning": "Patient explicitly stated previous negative healthcare experience related to sexual orientation, indicating medical mistrust and need for affirming care.",
  "recommendation": {{
    "(1) BACKGROUND & CONTEXT": {{ ... research LGBTQ+ healthcare disparities, discrimination patterns ... }},
    "(2) APPROACH": "... affirming opening acknowledging past harm ...",
    "(3) EXPLORE": [ ... questions about LGBTQ+ healthcare experiences ... ],
    "(4) INTEGRATE": [ ... specific LGBTQ+ affirming actions ... ],
    "(5) AVOID": [ ... heteronormative assumptions, invasive questions ... ]
  }}
}}

**DO NOT combine these into one flag.** Each dimension deserves detailed, specific recommendations.

**Other Examples of When to Create Multiple Flags:**
- Black + female + pregnant = Consider separate flags for (1) race-based maternal mortality disparities AND (2) gender-based pain dismissal
- Muslim + Arabic speaker = Consider separate flags for (1) Islamic religious practices AND (2) language/interpretation needs
- Indigenous + diabetes + rural location = Consider separate flags for (1) Indigenous health disparities AND (2) structural barriers (rural access, IHS underfunding)

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
      "flag": "Brief title of the equity-related insight (e.g., 'Risk of underestimating pain').",
      "reasoning": "Explain WHY this is relevant for this specific patient demographic, based on established health equity principles. Include relevant statistics or research if applicable to this group.",
      "recommendation": "This should be a DETAILED INFORMATION BOX teaching the doctor about this specific cultural/religious/demographic group and how to provide excellent care.
      
      **CRITICAL: Create a SEPARATE flag entry for EACH distinct dimension of identity the patient mentioned. If they mentioned being Buddhist AND being gay, create TWO separate flags with TWO separate recommendation boxes. DO NOT combine multiple identities into one flag.**
      
      Structure each recommendation as:

(1) BACKGROUND & CONTEXT: DO THE RESEARCH and provide comprehensive, specific information about this patient's cultural/religious/demographic group based on what THEY mentioned in the conversation. DO NOT just say "ask about X" - instead, PROVIDE the actual researched information about X.

   **Research Approach Examples (adapt to YOUR patient's actual context):**

   - If patient mentions a religion: Research specific religious practices affecting healthcare (prayer/worship schedules with times, fasting periods with dates, dietary laws with specific ingredients to check, modesty considerations, traditional healing practices with names and safety info, family involvement norms)

   - If patient mentions ethnicity + health condition: Research prevalence statistics for that condition in this population (exact percentages vs. general population), traditional foods and how to adapt them (not eliminate), common traditional remedies with scientific names and evidence, social determinants barriers (food access, language, insurance), culturally appropriate resources

   - If patient mentions past discrimination or is from group with documented disparities: Research specific disparity statistics (cite numbers and studies), historical medical trauma relevant to this group, implicit bias patterns documented in research, validated assessment tools to use, concrete bias-interruption techniques

   Be COMPREHENSIVE and SPECIFIC - provide actual facts, practices, medications, statistics, and cultural details the doctor needs to know. Tailor to what THIS specific patient mentioned in their conversation.

(2) APPROACH: How to open the conversation respectfully. Include exact phrases tailored to THIS scenario.

(3) EXPLORE: Provide SPECIFIC questions with CONTEXT about why to ask them and what answers to expect. Format each question with [explanation in brackets]. Tailor to what the patient mentioned. Examples of format:

   Instead of generic: "Ask about religious practices"
   Provide specific: "Ask: '[Specific question using appropriate religious/cultural terminology that shows you researched their background]' [This shows respect and addresses specific concern X that you learned about in your research]"

   Instead of generic: "Ask about diet"
   Provide specific: "Ask: '[Specific question about foods they might avoid, using correct cultural/religious terms]' [This helps identify if [specific ingredients] in medications need alternatives, and informs nutritional advice about [specific traditional foods they likely eat]]"

   Provide 4-6 questions, each with context about why it matters and what answers you expect based on your research of this specific cultural/religious/ethnic group.

(4) INTEGRATE: Provide concrete, specific actions based on what you researched about this patient's context. Examples:
   - If religious practices mentioned: Specific scheduling accommodations (times to avoid, days to avoid, how to adjust)
   - If dietary laws mentioned: Specific medication ingredients to review with pharmacy, specific alternatives to suggest
   - If traditional medicine mentioned: How to safely integrate (which herbs/practices, what drug interactions to check)
   - If disparities exist: Specific validated tools to use, specific bias-interruption techniques
   - If language barriers: Specific resources (interpreter services, translated materials in appropriate language)
   
   Provide 5-8 concrete actions tailored to THIS patient's specific context.

(5) AVOID: Common mistakes or biases specific to interacting with THIS group."
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

CRITICAL REMINDERS:
1. **Multiple Identity Dimensions = Multiple Flags:** If the patient mentioned being Buddhist AND gay AND had discrimination, create at least 2-3 separate equity_and_context_flags entries (one for religious identity, one for LGBTQ+ identity, one for past discrimination/medical mistrust). Each gets its own detailed recommendation box.

2. **Capture ALL aspects of patient's answer:** When the patient answers the empowerment question, parse their ENTIRE response carefully. Don't focus on just one aspect - identify ALL dimensions of identity, experience, and context they shared.

3. **Respond with ONLY the JSON object.** No additional text before or after."""

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
            equity_and_context_flags=briefing_data.get("equity_and_context_flags", []),
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
