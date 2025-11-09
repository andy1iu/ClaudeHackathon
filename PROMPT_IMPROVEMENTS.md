# Clinical Prompt Improvements - Health Equity Edition

## Overview

This document describes the major improvements made to both the **conversational intake prompt** and the **clinical synthesis prompt** to enhance clinical quality, health equity awareness, and diagnostic precision.

---

## 🎯 Key Improvements

### 1. **Enhanced Conversational Prompt** (`build_conversational_prompt`)

#### **What Changed:**
- **Persona Introduction**: The AI now introduces itself as "Amani," a highly skilled, patient-centered AI intake specialist
- **Clinical Framework (OPQRST-based)**: The AI now follows a structured clinical interview toolkit:
  - **Chief Complaint**: Main reason for visit
  - **Onset**: When symptoms started
  - **Quality/Character**: Description of symptoms (sharp, dull, throbbing, etc.)
  - **Severity**: Impact on daily life
  - **Timing/Frequency**: Pattern of occurrence
  - **Associated Symptoms**: Related symptoms
  
- **The Empowerment Question**: After gathering clinical details, the AI MUST ask:
  > "Thank you, that's very clear. Lastly, and this is just as important, is there anything about your personal beliefs, cultural background, or past experiences with healthcare that you would like your doctor to be aware of when considering your care?"

- **Enhanced Conversational Flow**:
  - Warm, reassuring persona with validation statements
  - One question at a time for better pacing
  - Brief responses (1-2 sentences)
  - Clear completion signal after empowerment question

#### **Benefits:**
✅ More structured, clinically comprehensive intake  
✅ Captures sociocultural context that impacts care  
✅ Better patient experience with empathetic validation  
✅ Ensures critical clinical details aren't missed

---

### 2. **Advanced Synthesis Prompt** (`synthesize_from_conversation`)

#### **What Changed:**

##### **Critical Guiding Principles** (NEW)
The prompt now explicitly includes health equity guardrails:
1. **Context, Not Causation**: Race/ethnicity are social constructs, not biological determinants
2. **Augment, Don't Diagnose**: Surface insights to augment clinician judgment
3. **Evidence-Based**: All insights must be directly supported by data

##### **Structured Analysis Framework** (NEW)
The AI now follows a 4-step reasoning process:

**Step 1: Synthesize Chief Complaint**  
Create a concise clinical summary

**Step 2: Deep Clinical Analysis**  
Cross-reference conversation with EHR:
- **Drug-Symptom Correlations**: Could symptoms be medication side effects?
- **Condition Progression**: Do symptoms suggest worsening chronic conditions?
- **Treatment Gaps**: Is current treatment ineffective?

**Step 3: Health Equity Analysis**  
Consider systemic and cultural factors:
- **Bias Interruption**: Are symptoms often dismissed in this demographic?
- **Population Health Risks**: Higher prevalence conditions to consider?
- **Cultural Context**: Patient's stated beliefs/experiences

**Step 4: Generate Structured JSON Output**

##### **Enhanced JSON Schema** (NEW)
The output now includes:

```json
{
  "ai_summary": "Clinical summary",
  
  "key_insights_flags": [
    {
      "type": "Medication Side Effect | Condition Progression | Treatment Efficacy | Risk | Alert",
      "flag": "Brief title",
      "reasoning": "Evidence-based explanation",
      "severity": "Low | Medium | High"  // NEW
    }
  ],
  
  "equity_and_context_flags": [  // NEW SECTION
    {
      "type": "Bias Interruption | Population Health | Cultural Context",
      "flag": "Brief title",
      "reasoning": "Why this matters for this patient",
      "recommendation": "Concrete action for clinician"
    }
  ],
  
  "reported_symptoms_structured": [...],
  "relevant_history_surfaced": [...]
}
```

#### **Benefits:**
✅ Explicit health equity analysis  
✅ Separation of clinical vs. sociocultural insights  
✅ Actionable recommendations for clinicians  
✅ Severity ratings for triaging  
✅ Deep medication-symptom correlation analysis

---

## 📊 Database & Schema Changes

### Database Model Updates
**File**: `backend/app/models/patient.py`

Added new column to `ClinicalBriefing` table:
```python
equity_and_context_flags = Column(JSON, nullable=True)
```

### Pydantic Schema Updates
**File**: `backend/app/schemas/patient.py`

1. **Enhanced `KeyInsightFlag`** with severity field:
```python
class KeyInsightFlag(BaseModel):
    type: str
    flag: str
    reasoning: str
    severity: Optional[str] = None  # NEW
```

2. **New `EquityContextFlag`** model:
```python
class EquityContextFlag(BaseModel):
    type: str
    flag: str
    reasoning: str
    recommendation: str  # NEW
```

3. **Updated `ClinicalBriefingBase`**:
```python
class ClinicalBriefingBase(BaseModel):
    # ... existing fields ...
    equity_and_context_flags: Optional[List[EquityContextFlag]] = None  # NEW
```

---

## 🎨 Frontend Enhancements

### BriefingView Component Updates
**File**: `frontend/src/components/BriefingView.jsx`

#### New Features:
1. **Severity Badges**: Visual indicators for Low/Medium/High severity
   - Low: Green badge
   - Medium: Orange badge
   - High: Red badge

2. **Health Equity Section**: New purple-themed section displaying:
   - Equity flag type (Bias Interruption, Population Health, Cultural Context)
   - Reasoning for why it matters
   - Actionable recommendation in highlighted box

3. **Enhanced Icons**: Support for new flag types (Medication Side Effect, Condition Progression, etc.)

---

## 🔄 Migration

### Migration Script
**File**: `backend/migrate_equity_context_flags.py`

Adds the `equity_and_context_flags` column to existing databases.

**To run:**
```bash
cd backend
source venv/bin/activate
python migrate_equity_context_flags.py
```

---

## 🧪 Testing the Changes

### 1. Test the Enhanced Conversation Flow
1. Reset briefings: `python backend/reset_briefings.py`
2. Start a new patient intake
3. Verify that "Amani" introduces herself
4. Observe structured questioning (onset, quality, severity, etc.)
5. Confirm the empowerment question is asked
6. Verify completion signal

### 2. Test the Health Equity Analysis
1. Complete an intake for a patient from an underrepresented demographic
2. View the generated briefing
3. Check for:
   - Severity badges on clinical flags
   - Purple "Health Equity & Patient Context" section
   - Actionable recommendations

### 3. Test Medication-Symptom Analysis
1. Complete an intake where a patient mentions a symptom that could be a side effect
2. Verify the briefing flags the potential correlation
3. Check that it references specific medications from EHR

---

## 📈 Expected Outcomes

### Clinical Quality
- ✅ More comprehensive symptom documentation
- ✅ Better medication side effect detection
- ✅ Clearer condition progression tracking
- ✅ Actionable clinical insights with severity levels

### Health Equity
- ✅ Explicit consideration of systemic bias risks
- ✅ Population health context
- ✅ Cultural competency through patient-stated preferences
- ✅ Concrete recommendations to interrupt bias

### Patient Experience
- ✅ More empathetic, validating conversation
- ✅ Better pacing (one question at a time)
- ✅ Opportunity to share cultural context
- ✅ Feeling heard and understood

### Clinician Experience
- ✅ Structured, scannable briefings
- ✅ Clear separation of clinical vs. equity insights
- ✅ Actionable next steps
- ✅ Risk stratification via severity levels
- ✅ More complete clinical picture

---

## 🔐 Safety & Ethics

### Health Equity Guardrails
The prompts now include explicit instructions to:
- **NEVER** treat race/ethnicity as biological causation
- **ALWAYS** consider social determinants of health
- **ONLY** use demographic data to surface potential bias risks
- **DEFER** all diagnostic decisions to human clinicians

### Validation & Evidence Requirements
Every insight must:
- Be directly supported by conversation or EHR data
- Cite specific evidence
- Avoid speculation
- Augment (not replace) clinical judgment

---

## 📝 Files Modified

### Backend
- ✅ `backend/app/api/chat.py` - Enhanced conversation & synthesis prompts
- ✅ `backend/app/api/synthesize.py` - Added equity flags support
- ✅ `backend/app/models/patient.py` - Added equity_and_context_flags column
- ✅ `backend/app/schemas/patient.py` - Added EquityContextFlag model & severity field

### Frontend
- ✅ `frontend/src/components/BriefingView.jsx` - Added equity section & severity badges

### Scripts
- ✅ `backend/migrate_equity_context_flags.py` - Database migration script
- ✅ `backend/reset_briefings.py` - Briefing reset utility (already existed)

---

## 🚀 Next Steps

### Immediate Actions
1. ✅ Database migration completed
2. ✅ Backend prompts updated
3. ✅ Frontend UI updated
4. ⏭️ Test with diverse patient scenarios
5. ⏭️ Gather clinician feedback on equity recommendations

### Future Enhancements
- [ ] Add analytics on equity flag frequency
- [ ] Integrate with clinical guidelines for population health
- [ ] Add customizable equity frameworks by specialty
- [ ] Multi-language support for empowerment question
- [ ] Patient-facing summary of their conversation

---

## 📞 Support

If you encounter any issues:
1. Check that the database migration ran successfully
2. Verify the backend server restarted after changes
3. Clear browser cache for frontend updates
4. Review `backend.log` for API errors

---

**Version**: 2.0  
**Date**: November 8, 2025  
**Author**: Prompt Engineering Improvements

