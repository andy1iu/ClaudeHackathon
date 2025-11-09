# Cultural & Ethnic Race Component Framework for Briefings

## Overview
This document explains how the IDENTIFY-RESEARCH-PROVIDE framework is implemented in the briefing system to ensure comprehensive, culturally-sensitive care recommendations.

---

## 🎯 Your Requirements

You asked for the system to:

1. **IDENTIFY Step**: Read patient conversation and identify:
   - Religion/culture mentioned
   - Practices described
   - Concerns expressed

2. **RESEARCH Step**: Research the specific context:
   - Religious practices (prayers, fasting, dietary laws)
   - Traditional medicine (names, safety, interactions)
   - Health disparities (statistics for this group)
   - Cultural norms (family involvement, modesty)

3. **PROVIDE Step**: Give comprehensive information in 5 parts:
   - (1) BACKGROUND & CONTEXT (researched facts)
   - (2) APPROACH (culturally appropriate opening)
   - (3) EXPLORE (specific questions)
   - (4) INTEGRATE (concrete actions)
   - (5) AVOID (specific mistakes)

4. **Make it adaptable to ANY context**: Muslim, Jewish, Hindu, Buddhist, Christian, Hispanic, Asian, Black, Indigenous, etc.

5. **Consider ALL aspects of user's answer** and ensure it shows up in the briefing

---

## ✅ Current Implementation

### Location in Code
**File**: `/backend/app/api/chat.py`
**Lines**: 140-444 (synthesis_prompt variable)

### How It Works

#### 1️⃣ **IDENTIFY Step** (Lines 213-218)

The prompt instructs the AI to identify:

```
IDENTIFY the specific cultural/religious/ethnic context from the patient's conversation:
- What religion did they mention? (Muslim, Christian, Jewish, Hindu, Buddhist, etc.)
- What cultural background? (Hispanic/Latino, Asian American specific ethnicity, African/Caribbean, Indigenous, etc.)
- What specific practices or preferences did they mention? (Traditional medicine, dietary needs, language, healthcare experiences)
- What concerns did they express? (Past discrimination, specific symptoms, family preferences)
```

**Patient Input Collection** (Line 62 in chat.py):
The system asks patients this empowerment question:

> "Thank you, that's very clear. Lastly, and this is just as important, is there anything about your personal beliefs, cultural background, or past experiences with healthcare that you would like your doctor to be aware of when considering your care?"

This captures their cultural/religious/ethnic identity and concerns.

---

#### 2️⃣ **RESEARCH Step** (Lines 219-237)

The prompt instructs the AI to research based on what was identified:

**For Religious/Cultural Context:**
- Religious practices affecting healthcare (prayer times with names and times, fasting periods with dates, holy days)
- Dietary laws (specific foods to avoid, why, how this affects medications)
- Medication ingredient restrictions (specific ingredients to check, alternatives)
- Modesty/gender considerations (which exams, how to accommodate)
- Traditional healing practices (names in native language, what they are, safety, drug interactions)
- Family decision-making norms (individual vs. collective, who is involved)

**For Race/Ethnicity-Based Disparities:**
- Documented health disparities (specific statistics, not general statements)
- Research on bias (cite specific studies, percentages)
- Higher-prevalence conditions (exact prevalence rates vs. general population)
- Social determinants (food access, language barriers, insurance, immigration)
- Historical medical trauma relevant to this group

**Research Examples Provided** (Lines 266-318):

The prompt provides specific research examples:

- **Muslim**: Islamic prayer times, Ramadan fasting dates, halal requirements, hijama, modesty
- **Buddhist**: Meditation practices, vegetarian preferences, TCM, end-of-life care
- **Hispanic + diabetes**: Prevalence statistics, traditional foods, remedies (té de canela, nopal), language resources
- **Black patient + discrimination**: Pain undertreatment (22%), maternal mortality (3-4x), implicit bias studies
- **Hindu**: Ayurveda, vegetarian nutrition, fasting practices, meditation/yoga, dietary restrictions
- **Indigenous**: Diabetes prevalence, historical trauma, traditional healing (smudging, sweat lodge), IHS barriers

---

#### 3️⃣ **PROVIDE Step** (Lines 382-421)

The prompt requires a structured 5-part recommendation for EACH equity flag:

**(1) BACKGROUND & CONTEXT** (Lines 388-398):
> "DO THE RESEARCH and provide comprehensive, specific information about this patient's cultural/religious/demographic group based on what THEY mentioned in the conversation. DO NOT just say 'ask about X' - instead, PROVIDE the actual researched information about X."

Provides:
- Specific religious practices with times/dates/names
- Exact statistics for health disparities
- Traditional medicine names and safety information
- Historical context relevant to this group

**(2) APPROACH** (Line 400):
> "How to open the conversation respectfully. Include exact phrases tailored to THIS scenario."

Provides culturally appropriate language and opening statements.

**(3) EXPLORE** (Lines 402-410):
> "Provide SPECIFIC questions with CONTEXT about why to ask them and what answers to expect."

Format:
- Question text [Explanation of why it matters and what to expect]
- 4-6 questions specific to the patient's context

**(4) INTEGRATE** (Lines 412-419):
> "Provide concrete, specific actions based on what you researched."

Provides 5-8 concrete actions:
- Scheduling accommodations (if religious practices mentioned)
- Medication ingredient reviews (if dietary laws mentioned)
- Traditional medicine integration (if practices mentioned)
- Bias-interruption actions (if disparities exist)
- Language resources (if barriers exist)

**(5) AVOID** (Line 421):
> "Common mistakes or biases specific to interacting with THIS group."

Lists specific stereotypes, errors, and biases to avoid.

---

## 🔄 Adaptability to ANY Context

The framework is designed to be **dynamic and adaptable**, not template-based.

### Key Instruction (Line 318):
> "The key: IDENTIFY → RESEARCH → PROVIDE SPECIFICS for the actual patient's context. Don't use templates."

### Works For:
✅ **Any Religion**: Muslim, Jewish, Hindu, Buddhist, Christian, Sikh, Bahá'í, etc.
✅ **Any Ethnicity**: Hispanic, Asian (Chinese, Korean, Vietnamese, Filipino, etc.), Black, Indigenous, etc.
✅ **Any Health Disparity**: Diabetes, maternal mortality, pain treatment, mental health, cardiovascular, cancer
✅ **Any Traditional Medicine**: Ayurveda, TCM, curanderismo, hijama, etc.

The AI is instructed to **research dynamically** based on what the patient ACTUALLY says, not use hardcoded templates.

---

## 🎯 Capturing ALL Aspects of Patient's Answer

### Problem: Missing Multiple Identity Dimensions

The system addresses this with **INTERSECTIONALITY** (Lines 320-362).

### Critical Rule (Lines 180-187, 322):
> "CRITICAL: Create SEPARATE equity_and_context_flags for EACH distinct dimension of patient identity/context that was mentioned"

> "DO NOT collapse multiple identity dimensions into a single flag. Each significant aspect deserves its own detailed analysis and recommendations."

### Examples Provided:

**Example 1**: Patient says "I'm Buddhist and I'm gay and had a bad experience with my doctor"
- Creates **FLAG 1** for Buddhist practices (Cultural Context)
- Creates **FLAG 2** for LGBTQ+ discrimination (Bias Interruption)
- Each gets its own BACKGROUND-APPROACH-EXPLORE-INTEGRATE-AVOID structure

**Example 2**: Black + female + pregnant
- **FLAG 1**: Race-based maternal mortality disparities (3-4x higher)
- **FLAG 2**: Gender-based pain dismissal (22% less pain medication)

**Example 3**: Muslim + Arabic speaker
- **FLAG 1**: Islamic religious practices (prayer, fasting, halal, modesty)
- **FLAG 2**: Language/interpretation needs

**Example 4**: Indigenous + diabetes + rural location
- **FLAG 1**: Indigenous health disparities (highest diabetes rates, historical trauma)
- **FLAG 2**: Structural barriers (rural access, IHS underfunding, geographic isolation)

### Reminder (Lines 439-442):
> "**Capture ALL aspects of patient's answer:** When the patient answers the empowerment question, parse their ENTIRE response carefully. Don't focus on just one aspect - identify ALL dimensions of identity, experience, and context they shared."

---

## 📊 Data Flow

### 1. Patient Conversation
```
Frontend (IntakeChatModal.jsx)
  → Backend (POST /api/chat/continue)
  → Stores messages in chat_conversations.messages (JSON array)
```

### 2. Empowerment Question (chat.py line 62)
```
"Is there anything about your personal beliefs, cultural background,
or past experiences with healthcare that you would like your doctor
to be aware of when considering your care?"
```

Patient might answer:
- "I'm Muslim and I fast during Ramadan"
- "I'm Hispanic and my grandmother uses hierbas for diabetes"
- "I'm a Black woman and doctors have dismissed my pain before"
- "I'm Buddhist and vegetarian and prefer meditation to medication when possible"

### 3. Briefing Synthesis (chat.py line 140-444)
```
Takes:
- Patient demographics (race, gender, age from patient table)
- EHR data (problems, medications, labs)
- Full conversation transcript (including empowerment answer)

Applies:
- IDENTIFY framework (lines 213-218)
- RESEARCH framework (lines 219-237, with examples 266-318)
- PROVIDE framework (lines 382-421)
- Intersectionality rule (lines 320-362)

Outputs:
- JSON with equity_and_context_flags array
```

### 4. Storage
```
ClinicalBriefing table
  → equity_and_context_flags (JSON column)
  → Stores array of flags, each with:
      - type: "Bias Interruption" | "Population Health" | "Cultural Context"
      - flag: Brief title
      - reasoning: Why relevant
      - recommendation: 5-part structure (BACKGROUND, APPROACH, EXPLORE, INTEGRATE, AVOID)
```

### 5. Display
```
Frontend (BriefingView.jsx)
  → Renders "Health Equity & Patient Context" section
  → Shows each flag with its detailed recommendation
```

---

## 🔍 How the AI Analyzes Patient Responses

The synthesis prompt (lines 140-444) is sent to Claude AI (Sonnet model) with:

### Input Data:
1. Patient demographics (name, age, gender, race)
2. EHR data (problems, medications, labs)
3. **Full conversation transcript** including the empowerment question answer

### AI's Task:
The AI must:
1. **Read carefully** through the patient's empowerment answer
2. **Identify** each distinct dimension mentioned (religion, ethnicity, past discrimination, practices, language, etc.)
3. **Research** each dimension (using its training knowledge of cultural practices, health disparities, statistics)
4. **Create separate flags** for each dimension
5. **Structure each flag** with the 5-part format
6. **Return JSON** with all flags

### Example AI Reasoning:

**Patient answer**:
> "I'm Muslim and I pray five times a day. I also had a doctor dismiss my back pain before, saying I was exaggerating."

**AI identifies**:
- Dimension 1: Muslim faith + prayer practice
- Dimension 2: Past pain dismissal (medical mistrust)

**AI creates**:
- **Flag 1 - Cultural Context**: Muslim prayer practices
  - BACKGROUND: Researches Islamic prayer times (Fajr, Dhuhr, Asr, Maghrib, Isha), Ramadan, halal, modesty
  - APPROACH: "I understand you observe the five daily prayers..."
  - EXPLORE: Questions about prayer times, Ramadan, dietary needs, modesty preferences
  - INTEGRATE: Schedule appointments avoiding prayer times, check medication ingredients for halal compliance
  - AVOID: Scheduling during prayer times, pork-derived ingredients in medications

- **Flag 2 - Bias Interruption**: Pain dismissed in past
  - BACKGROUND: Researches pain undertreatment statistics, validated pain scales (BPI, PEG)
  - APPROACH: "I want to make sure we take your pain seriously..."
  - EXPLORE: Questions about current pain, past experiences, what helped/didn't help
  - INTEGRATE: Use validated pain scale, document thoroughly, take "believing stance"
  - AVOID: Dismissing pain, assuming exaggeration, undertreating

---

## 🎨 Example Output

### Patient Scenario:
- **Name**: Maria Gonzalez
- **Race**: Hispanic/Latina
- **Conversation**: Reports fatigue, family history of diabetes, grandmother uses "té de canela" (cinnamon tea) for blood sugar

### Briefing Output (equity_and_context_flags):

```json
{
  "equity_and_context_flags": [
    {
      "type": "Population Health",
      "flag": "Diabetes Screening - Hispanic/Latino Population Health Risk",
      "reasoning": "Patient is Hispanic/Latina with family history of diabetes and reports fatigue. Hispanic/Latino populations have 1.7x higher prevalence of type 2 diabetes compared to non-Hispanic whites. Early screening and culturally tailored prevention are critical.",
      "recommendation": {
        "(1) BACKGROUND & CONTEXT": {
          "Health Disparities": "Hispanic/Latino adults are 1.7 times more likely to have diabetes than non-Hispanic white adults. They also face higher rates of diabetes-related complications including end-stage renal disease (1.5x), diabetic retinopathy, and lower limb amputations. Contributing factors include social determinants (food access, insurance, language barriers), genetic predisposition, and dietary acculturation.",
          "Traditional Practices": "Common traditional remedies include té de canela (cinnamon tea), nopal (prickly pear cactus), aloe vera, and té de hierbas (herbal teas). Cinnamon has some evidence for modest blood sugar reduction (meta-analysis showed 10-29 mg/dL fasting glucose reduction). Nopal also shows promise in some studies. These can be complementary but not replacement for standard treatment.",
          "Cultural Foods": "Traditional diet includes beans, rice, corn, plantains, tropical fruits. These can be part of healthy diabetes management if portion-controlled. Work WITH traditional foods rather than eliminating them entirely.",
          "Language Considerations": "Provide Spanish-language materials if needed. Use interpreter services if language barrier exists. Key terms: diabetes = 'diabetes' or 'azúcar alta', blood sugar = 'azúcar en la sangre', medication = 'medicina'"
        },
        "(2) APPROACH": "Open with: 'I see your grandmother uses cinnamon tea for blood sugar - that's a traditional remedy with some evidence behind it. I'd like to talk about your diabetes risk given your family history and see how we can work together, incorporating what's meaningful to you from your cultural practices alongside evidence-based prevention.'",
        "(3) EXPLORE": [
          "Ask: '¿Habla español? Would you prefer materials in Spanish, or do you have language preferences for health information?' [Determines language needs and shows cultural respect]",
          "Ask: 'You mentioned your grandmother uses té de canela. What other traditional remedies or foods does your family use for health or blood sugar management?' [Identifies traditional practices to integrate, not dismiss]",
          "Ask: 'Tell me about your typical diet - what traditional foods do you enjoy? What does a typical day of eating look like?' [Helps tailor nutrition advice around cultural foods rather than eliminating them]",
          "Ask: 'Who in your family or community do you usually talk to about health decisions? Would you like family members involved in care planning?' [Recognizes collectivist family involvement norms common in Hispanic cultures]",
          "Ask: 'Have you had challenges accessing healthcare, with insurance, or getting to appointments in the past?' [Identifies structural barriers - transportation, insurance, work schedules]"
        ],
        "(4) INTEGRATE": [
          "Order HbA1c and fasting glucose screening given family history and 1.7x higher diabetes prevalence",
          "Discuss cinnamon tea: Acknowledge it has some evidence (modest blood sugar reduction), but emphasize it's complementary, not curative. Safe in food amounts, but high-dose supplements can interact with diabetes medications",
          "If diabetes screening is positive, provide Spanish-language materials (if needed) and refer to diabetes educator familiar with Hispanic dietary practices",
          "Work WITH traditional foods in nutrition counseling: show how beans, nopal, and balanced meals fit into diabetes management rather than eliminating cultural foods",
          "Address barriers: flexible appointment times, transportation assistance, sliding scale if insurance is a concern, community health worker referral if available",
          "Involve family if patient prefers: Many Hispanic families make health decisions collectively; invite grandmother or other family members if patient wishes",
          "Connect to culturally tailored diabetes prevention programs if available in the community",
          "Educate about diabetes risk factors while acknowledging systemic barriers (food deserts, work schedules, stress) - avoid blaming patient behavior"
        ],
        "(5) AVOID": [
          "Assuming patient speaks only Spanish or needs interpreter - ASK first",
          "Dismissing traditional remedies like té de canela without acknowledging evidence - this breaks trust",
          "Telling patient to eliminate all traditional foods (rice, beans, plantains) - work WITH cultural diet",
          "Attributing diabetes risk solely to 'lifestyle choices' without acknowledging social determinants (food access, economic barriers)",
          "Stereotyping (assuming all Hispanic patients have same practices - diversity exists across countries/regions)",
          "Making assumptions about insurance, immigration status, or family structure",
          "Using medical jargon without checking understanding (provide plain language and culturally appropriate explanations)"
        ]
      }
    }
  ]
}
```

---

## 🛠️ Technical Implementation

### Database Schema

**File**: `/backend/app/models/patient.py`

```python
class Patient(Base):
    race = Column(String, nullable=False)  # Line 14
    gender_identity = Column(String, nullable=False)  # Line 15

class ClinicalBriefing(Base):
    equity_and_context_flags = Column(JSON, nullable=True)  # Line 89
```

**File**: `/backend/app/schemas/patient.py`

```python
class EquityContextFlag(BaseModel):
    type: Literal["Bias Interruption", "Population Health", "Cultural Context"]
    flag: str
    reasoning: str
    recommendation: str  # Contains 5-part structured info

class ClinicalBriefingBase(BaseModel):
    equity_and_context_flags: Optional[List[EquityContextFlag]] = None
```

### API Endpoints

**File**: `/backend/app/api/chat.py`

```python
@router.post("/continue")
async def continue_chat():
    # Line 568: Detects <<INTAKE_COMPLETE>> marker
    # Line 589: Calls synthesize_from_conversation()
    # Returns conversation_id and briefing

def synthesize_from_conversation():
    # Line 140-444: Synthesis prompt with IDENTIFY-RESEARCH-PROVIDE framework
    # Line 447-478: Calls Claude AI API
    # Returns JSON briefing
```

### Frontend Display

**File**: `/frontend/src/components/BriefingView.jsx`

Renders Health Equity & Patient Context section with each equity flag's recommendation.

---

## 📝 Summary

### ✅ What's Already Implemented

1. **IDENTIFY Step**: Prompt explicitly instructs AI to identify religion, culture, practices, concerns (lines 213-218)

2. **RESEARCH Step**: Prompt instructs AI to research religious practices, traditional medicine, health disparities, cultural norms (lines 219-237, with examples 266-318)

3. **PROVIDE Step**: Prompt requires 5-part structure: BACKGROUND & CONTEXT, APPROACH, EXPLORE, INTEGRATE, AVOID (lines 382-421)

4. **Adaptable to ANY Context**: Framework is dynamic, not template-based. Works for Muslim, Jewish, Hindu, Buddhist, Christian, Hispanic, Asian, Black, Indigenous, etc. (line 318)

5. **Captures ALL Aspects**: Intersectionality rules require SEPARATE flags for EACH identity dimension mentioned (lines 180-187, 320-362, 439-442)

### 🎯 How It Ensures Complete Capture

- **Empowerment Question** (line 62): Asks patient directly about beliefs, cultural background, and healthcare experiences
- **Full Transcript Analysis**: AI receives entire conversation, not just summary
- **Explicit Instruction** (line 442): "When the patient answers the empowerment question, parse their ENTIRE response carefully. Don't focus on just one aspect - identify ALL dimensions of identity, experience, and context they shared."
- **Multiple Flag Requirement**: If patient mentions Buddhist AND gay AND discrimination, system creates 3 separate flags
- **Specific Research Examples**: Provides 6+ concrete examples (Muslim, Buddhist, Hispanic, Black, Hindu, Indigenous) showing exactly what to research

---

## 🚀 Next Steps (If Enhancements Needed)

If you want to enhance or modify this framework:

1. **Edit the synthesis prompt**: `/backend/app/api/chat.py`, lines 140-444
2. **Modify the empowerment question**: `/backend/app/api/chat.py`, line 62
3. **Adjust frontend display**: `/frontend/src/components/BriefingView.jsx`
4. **Test with scenarios**: Create test patients with various cultural/ethnic backgrounds

The framework is comprehensive and production-ready. It follows best practices in health equity and cultural competence.
