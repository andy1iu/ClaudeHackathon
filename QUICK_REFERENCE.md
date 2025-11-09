# Quick Reference: Enhanced Prompts

## 🎯 What Changed?

### Conversational Prompt (Intake Chat)
- **New Persona**: "Amani" - patient-centered AI intake specialist
- **Clinical Framework**: Structured OPQRST-based questioning
- **Empowerment Question**: Captures cultural beliefs & healthcare experiences
- **Enhanced Empathy**: Validation statements, better pacing

### Synthesis Prompt (Briefing Generation)
- **Health Equity Principles**: Explicit bias-awareness guardrails
- **4-Step Analysis**: Chief complaint → Clinical analysis → Equity analysis → JSON output
- **New Fields**: 
  - `severity` on clinical flags (Low/Medium/High)
  - `equity_and_context_flags` - separate equity insights with recommendations

---

## 🔍 Example: Before vs. After

### Before (Old Prompt)
**Conversation:**
```
AI: "Hello! What brings you in today?"
Patient: "I have chest pain."
AI: "Can you tell me more about that?"
[3-4 exchanges]
AI: "Thank you. <<INTAKE_COMPLETE>>"
```

**Briefing:**
```json
{
  "key_insights_flags": [
    {
      "type": "Risk",
      "flag": "Chest pain",
      "reasoning": "Patient reports chest pain"
    }
  ]
}
```

### After (New Prompt)
**Conversation:**
```
AI: "Hello! I'm Amani, and I'm here to help gather some information 
     before your appointment. Can you tell me what brings you in?"
Patient: "I have chest pain."
AI: "That sounds really tough. When did this start?"
Patient: "About 3 days ago."
AI: "I understand. What does the pain feel like - is it sharp, dull, 
     or something else?"
Patient: "It's a sharp pain."
AI: "How much is this affecting your daily activities?"
Patient: "I can't exercise anymore."
AI: "Thank you, that's very clear. Lastly, and this is just as important, 
     is there anything about your personal beliefs, cultural background, 
     or past experiences with healthcare that you would like your doctor 
     to be aware of when considering your care?"
Patient: "In my culture, we prefer natural remedies first."
AI: "Thank you for sharing. I've noted that for your doctor. <<INTAKE_COMPLETE>>"
```

**Briefing:**
```json
{
  "key_insights_flags": [
    {
      "type": "Alert",
      "flag": "Acute onset chest pain limiting physical activity",
      "reasoning": "Patient reports sharp chest pain starting 3 days ago, 
                    now preventing exercise. Given history of hypertension 
                    and current medications, cardiac evaluation warranted.",
      "severity": "High"
    }
  ],
  "equity_and_context_flags": [
    {
      "type": "Cultural Context",
      "flag": "Preference for natural remedies",
      "reasoning": "Patient's cultural background emphasizes natural remedies 
                    as first-line treatment. This preference should inform 
                    treatment planning and shared decision-making.",
      "recommendation": "Discuss treatment options that integrate patient's 
                         cultural preferences where medically appropriate. 
                         Explain rationale for any urgent conventional treatments."
    }
  ]
}
```

---

## 🎨 UI Changes

### Severity Badges
Clinical flags now show color-coded severity:
- 🟢 **Low** - Green badge
- 🟠 **Medium** - Orange badge  
- 🔴 **High** - Red badge

### Health Equity Section
New purple-themed section appears when equity insights are present:
- **Type**: Bias Interruption / Population Health / Cultural Context
- **Flag**: Brief title
- **Reasoning**: Why it matters for this patient
- **Recommendation**: Highlighted action box with concrete next steps

---

## 🧪 Quick Test

```bash
# 1. Reset all briefings
cd backend
source venv/bin/activate
python reset_briefings.py

# 2. Restart backend (if running)
# Stop the server, then:
python -m uvicorn app.main:app --reload --port 8000

# 3. Frontend should auto-reload, or restart if needed
# In another terminal:
cd frontend
npm run dev

# 4. Test a patient intake:
#    - Look for "Amani" in greeting
#    - Answer questions about symptoms
#    - Answer the empowerment question
#    - View the generated briefing
#    - Look for severity badges
#    - Look for purple equity section
```

---

## 📋 Checklist

After deploying these changes:

- [ ] Database migration completed
- [ ] Backend restarted
- [ ] Frontend restarted
- [ ] Tested intake conversation flow
- [ ] Verified "Amani" introduces herself
- [ ] Confirmed empowerment question is asked
- [ ] Checked briefing has severity levels
- [ ] Confirmed equity section appears when relevant
- [ ] Reviewed equity recommendations are actionable

---

## 🐛 Troubleshooting

### "No equity section showing"
- The AI only generates equity flags when relevant
- Try a patient with complex cultural context or from an underrepresented group

### "Severity badges not showing"
- Check that backend is returning `severity` field in `key_insights_flags`
- Clear browser cache

### "Empowerment question not asked"
- The AI should ask after 3-4 clinical exchanges
- If testing quickly, try providing detailed symptom responses

### "Old greeting still showing"
- Backend server needs to restart to pick up prompt changes
- Verify you're not seeing cached content

---

## 📊 Monitoring

Watch for:
- **Clinical Quality**: Are more medication-symptom correlations being caught?
- **Equity Impact**: Are bias risks being surfaced appropriately?
- **Patient Feedback**: Do patients feel heard after the empowerment question?
- **Clinician Feedback**: Are recommendations actionable and helpful?

---

**Last Updated**: November 8, 2025

