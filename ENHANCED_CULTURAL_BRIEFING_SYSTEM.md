# Enhanced Cultural Briefing System - IDENTIFY → RESEARCH → PROVIDE

## Overview

The clinical briefing system has been enhanced with a comprehensive **3-step framework** for generating culturally informed, equity-focused recommendations. This ensures that ALL aspects of a patient's cultural, religious, ethnic, and identity-related context are captured and presented to clinicians with actionable, researched guidance.

---

## The 3-Step Framework

### STEP 1: IDENTIFY
**Read the patient's conversation and identify what they mentioned**

The AI carefully reviews the entire patient conversation (especially the empowerment question response) and identifies:

- **Religion/Spiritual Identity**: Muslim, Christian, Jewish, Hindu, Buddhist, Sikh, Indigenous spirituality, etc.
- **Cultural/Ethnic Background**: Hispanic/Latino (with specific origin), Asian American (with specific ethnicity), African/Caribbean, Indigenous (with tribe/nation), Middle Eastern, etc.
- **LGBTQ+ Identity**: Sexual orientation, gender identity, chosen family preferences
- **Past Healthcare Experiences**: Discrimination, dismissal, medical mistrust
- **Traditional Medicine/Cultural Practices**: Specific practices, remedies, preferences mentioned
- **Family Dynamics**: Family involvement in decisions, caregiver roles
- **Structural Barriers**: Language barriers, transportation, insurance, immigration concerns
- **Symptom-Specific Disparities**: Race/ethnicity-based disparities relevant to presenting symptoms

**Key Rule**: Do NOT collapse or skip any dimension. Each distinct aspect gets identified separately.

---

### STEP 2: RESEARCH
**For EACH identified dimension, conduct comprehensive, specific research**

For every dimension identified in Step 1, the AI conducts detailed research tailored to what the patient actually mentioned:

#### For Religious/Spiritual Context:
- Prayer times (names in native language, typical times)
- Fasting periods (specific dates, duration, meal names/times, medication considerations)
- Dietary laws (prohibited foods/ingredients, why, impact on medications)
- Modesty considerations (which exams, how to accommodate)
- Traditional healing practices (names, description, safety, drug interactions)
- Family decision-making norms (individual vs. collective)
- Holy days/observances (dates to avoid scheduling)

#### For Race/Ethnicity Health Disparities:
- Specific statistics (e.g., "Black women experience maternal mortality at 3-4x rate of white women")
- Research on implicit bias (specific studies, percentages)
- Higher-prevalence conditions (exact rates vs. general population)
- Social determinants (food deserts, language barriers, insurance gaps, immigration)
- Historical medical trauma (specific events, ongoing impact)
- Validated assessment tools (names, how they reduce bias)

#### For Cultural Practices/Traditional Medicine:
- Name in native language and English
- What it is, how it's used
- Safety profile and evidence base
- Potential drug interactions
- How to respectfully integrate (not dismiss)

#### For LGBTQ+ Identity:
- Healthcare disparities statistics
- Appropriate terminology (pronouns, relationship terms)
- Specific health needs (hormone therapy, appropriate screening)
- Mental health considerations (minority stress statistics)
- Creating affirming environment

#### For Past Discrimination/Medical Mistrust:
- Common discrimination patterns (with statistics)
- Historical context contributing to mistrust
- Trust-building techniques (taking believing stance, shared decision-making)
- Validated assessment tools to reduce bias
- How to acknowledge and address past harm

**Key Rule**: Research must be SPECIFIC to what the patient mentioned, not generic. Use actual statistics, native terms, concrete details.

---

### STEP 3: PROVIDE
**Structure each flag with comprehensive 5-part framework**

For EACH distinct dimension identified in Step 1, create a SEPARATE `equity_and_context_flag` with this structure:

#### **(1) BACKGROUND & CONTEXT**
Comprehensive, researched information about this specific cultural/religious/demographic group.

**Include:**
- Specific practices, beliefs, traditions (with native language terms)
- Specific statistics and disparity data (actual numbers, not general statements)
- Historical context relevant to this group's healthcare experiences
- Evidence-based information about traditional medicine, dietary laws, cultural norms
- Must be SPECIFIC to what patient mentioned, not generic

**Example**: Instead of "Muslims may have dietary restrictions," provide: "Islamic dietary law (halal) prohibits pork and alcohol, including in medications (check gelatin capsules, alcohol-based syrups). During Ramadan (dates vary yearly based on lunar calendar), Muslims fast from dawn (Fajr) to sunset (Maghrib) - no food, water, or oral medications. Pre-dawn meal (Suhoor) and breaking fast (Iftar) are key times for medication timing adjustments..."

#### **(2) APPROACH**
Culturally appropriate opening phrases the doctor can use.

**Include:**
- Exact phrases acknowledging patient's specific preferences
- Appropriate cultural/religious terminology
- Language demonstrating respect, cultural humility, openness
- 2-3 specific opening statements tailored to THIS patient's context

**Example**: "I appreciate you sharing that you practice Islam and are currently observing Ramadan. I want to make sure we respect your fasting practices while ensuring you get the care you need. Can we discuss how to adjust your medication schedule around Suhoor and Iftar?"

#### **(3) EXPLORE**
4-6 specific questions with FULL CONTEXT in this format:
- "Question text using appropriate terminology?" [Why this matters and what answers to expect]

**Example**:
- "What time do you typically have Suhoor (pre-dawn meal) and Iftar (breaking fast)?" [Essential for timing medications during Ramadan; typical times are 4-5am and 7-9pm depending on season and location]
- "Would you prefer a same-gender provider for intimate examinations?" [Many Muslim patients prefer this for modesty; having female providers available for female patients shows cultural awareness]
- "Are you taking any herbal supplements or traditional remedies like black seed oil (Habbatus Sauda) or hijama (cupping therapy)?" [Common in Muslim communities; need to check for drug interactions]

#### **(4) INTEGRATE**
5-8 concrete, actionable steps tailored to THIS patient's specific context.

**Examples:**
- If religious practices → "Schedule appointments after 10am during Ramadan to avoid conflict with dawn prayer and Suhoor"
- If dietary laws → "Review all medications with pharmacy for gelatin, alcohol content; suggest alternatives (gel caps → tablets, elixirs → capsules)"
- If traditional medicine → "Ask about use of black seed oil; research shows potential blood sugar effects - monitor if diabetic, possible interaction with metformin"
- If disparities exist → "Use Brief Pain Inventory (BPI) tool to quantify pain; document thoroughly to counteract implicit bias in pain assessment"
- If language barriers → "Arrange for medical interpreter for all visits; provide translated discharge instructions in Arabic"

#### **(5) AVOID**
4-6 specific mistakes or biases relevant to THIS group.

**Examples:**
- "Don't ask patient to break Ramadan fast for non-emergency medications - work around fasting schedule instead"
- "Don't assume all Muslims speak Arabic (many are South Asian, African, Indonesian, American-born)"
- "Don't dismiss hijama/cupping as 'alternative medicine' - acknowledge it as part of patient's health practices and ask about it"
- "Don't schedule non-urgent procedures during Ramadan without discussing with patient"
- "Don't make assumptions about conservatism based on hijab - patients have wide range of practices and preferences"

---

## Key Implementation Rules

### 1. Multiple Dimensions = Multiple Flags
If a patient mentions being **Buddhist AND gay AND had past discrimination**, create **3 SEPARATE flags**:
- Flag 1: Buddhist Patient - Spiritual and Cultural Considerations
- Flag 2: LGBTQ+ Patient with Past Healthcare Discrimination
- Flag 3: Medical Mistrust and Trust-Building Strategies

**DO NOT** combine these into one flag. Each dimension deserves detailed, specific recommendations.

### 2. Capture ALL Aspects of Patient's Answer
When the patient answers the empowerment question ("is there anything about your personal beliefs, cultural background, or past experiences with healthcare that you would like your doctor to be aware of?"), parse their ENTIRE response.

**Example Patient Response**: "Well, I'm Muslim and currently fasting for Ramadan, and I'm also gay, and I had a really bad experience with a doctor who didn't believe my pain before."

**Required Output**: Create 3 separate flags:
1. Islamic Religious Practices - Ramadan Fasting Accommodations
2. LGBTQ+ Identity - Affirming Care Considerations
3. Past Pain Dismissal - Bias Interruption and Trust Building

### 3. Research Must Be Context-Specific
- Patient mentions "fasting" → Research the SPECIFIC religious fasting they mentioned (Ramadan, Yom Kippur, Lent, etc.)
- Patient mentions "Asian" → Ask for specifics and research that specific ethnicity (Vietnamese, Korean, Chinese, Filipino, etc. have different health disparities and cultural practices)
- Patient mentions "traditional medicine" → Research the SPECIFIC practice mentioned (curanderismo, Ayurveda, TCM, etc.)

**Don't use generic templates. Research and provide specific information.**

### 4. Use the Full 5-Part Structure for Every Flag
Every `equity_and_context_flag` must include a `recommendation` object with all 5 parts:
- (1) BACKGROUND & CONTEXT
- (2) APPROACH
- (3) EXPLORE
- (4) INTEGRATE
- (5) AVOID

No shortcuts. Each part must be comprehensive and actionable.

---

## Technical Implementation

### Backend Changes (`backend/app/api/chat.py`)

1. **Enhanced synthesis prompt** with explicit 3-step framework (IDENTIFY → RESEARCH → PROVIDE)
2. **Detailed research guidance** for each type of identity/context dimension
3. **Clear 5-part structure** for every recommendation
4. **Multiple flag requirement** for multiple identity dimensions
5. **Increased max_tokens** from 2000 to 4000 to accommodate comprehensive responses
6. **Concrete examples** showing how to apply the framework (Muslim, Black + pain, Hispanic + diabetes, LGBTQ+, Buddhist)

### Frontend Display (`frontend/src/components/BriefingView.jsx`)

The existing component already handles the enhanced recommendation structure:
- Displays `recommendation` as an object with the 5 parts
- Handles both string and object formats for backward compatibility
- Shows arrays (for EXPLORE and INTEGRATE and AVOID) as bulleted lists
- Formats nested objects appropriately
- Presents recommendations in a visually distinct purple/lavender info box

---

## Example Outputs

### Example 1: Muslim Patient Observing Ramadan

**Flag Type**: Cultural Context
**Flag Title**: Islamic Religious Practices - Ramadan Fasting Accommodations
**Reasoning**: Patient identifies as Muslim and is currently observing Ramadan, which involves dawn-to-sunset fasting that affects medication timing and appointment scheduling.

**Recommendation**:

**(1) BACKGROUND & CONTEXT**: Islamic dietary law (halal) prohibits pork and alcohol, including in medications. During Ramadan (dates vary yearly based on lunar calendar), Muslims fast from dawn (Fajr prayer, ~5:30am in summer) to sunset (Maghrib prayer, ~8:30pm in summer) - no food, water, or oral medications. Pre-dawn meal (Suhoor) ~4:30am and breaking fast (Iftar) ~8:30pm are key times for medication timing. Modesty is important: many Muslim women prefer same-gender providers for intimate exams and wear hijab (head covering). Traditional practices include hijama (cupping therapy) and use of black seed oil (Habbatus Sauda). Family involvement in healthcare decisions is common. Five daily prayers (Fajr dawn, Dhuhr noon, Asr afternoon, Maghrib sunset, Isha night) - appointments after morning prayers preferred. Friday (Jumu'ah) prayer at midday is important for observant Muslims.

**(2) APPROACH**: "I appreciate you sharing that you're observing Ramadan. I want to make sure we respect your fasting practices while ensuring you get the best care. Can we discuss how to adjust your medication schedule around your Suhoor and Iftar times?"

**(3) EXPLORE**:
- "What time do you typically have Suhoor (pre-dawn meal) and Iftar (breaking fast)?" [Essential for timing medications during Ramadan; typical times are 4-5am and 7-9pm]
- "Would you prefer a same-gender provider for any intimate examinations?" [Many Muslim patients prefer this for modesty; having female providers available shows cultural awareness]
- "Are you taking any herbal supplements or traditional remedies like black seed oil (Habbatus Sauda) or receiving hijama (cupping therapy)?" [Common in Muslim communities; need to check for drug interactions]
- "How do your family members typically participate in healthcare decisions?" [Collective decision-making is common; understanding family structure helps communication]
- "Are there specific times that work better for appointments around your prayer schedule?" [Five daily prayers - understanding this shows respect and improves adherence]

**(4) INTEGRATE**:
- Adjust medication schedule: Consolidate doses to Suhoor (~4:30am) and Iftar (~8:30pm) times during Ramadan
- Review all medications with pharmacy for gelatin (from pork) and alcohol content; suggest alternatives
- Offer same-gender provider option for intimate exams; document preference in chart
- Schedule appointments after 10am (after morning prayers) and avoid Friday midday (Jumu'ah prayer time)
- Ask about traditional practices (hijama, black seed oil) and research interactions - don't dismiss
- Involve family members in discussions if patient prefers (ask permission first)
- Provide medication timing sheet with Suhoor/Iftar times for current month of Ramadan
- Note Ramadan dates for next year to proactively adjust care

**(5) AVOID**:
- Don't ask patient to break Ramadan fast for non-emergency medications - work around fasting schedule
- Don't assume all Muslims speak Arabic (many are South Asian, African, Indonesian, American-born)
- Don't dismiss hijama/cupping as 'alternative medicine' without understanding its use
- Don't schedule non-urgent procedures during Ramadan without discussing with patient
- Don't make assumptions about conservatism based on hijab - wide range of practices
- Don't ask invasive questions about religious practice - let patient guide level of detail

### Example 2: Black Female Patient with Pain Symptoms

**Flag Type**: Bias Interruption
**Flag Title**: Pain Assessment in Black Female Patient - Bias Interruption Protocol
**Reasoning**: Patient is Black female presenting with pain symptoms. Research shows Black patients are 22% less likely to receive pain medication and report pain dismissal at significantly higher rates due to false biological beliefs and implicit bias.

**Recommendation**:

**(1) BACKGROUND & CONTEXT**: Black patients experience significant pain care disparities: 22% less likely to receive pain medication (Todd et al.), pain severity ratings given less credence, longer wait times for pain treatment, higher rates of pain undertreatment in emergency settings. False beliefs persist among healthcare providers that Black patients have "thicker skin" or "higher pain tolerance" (Hoffman et al. 2016) - these are completely false and rooted in historical racism. Black women specifically report having their pain dismissed or attributed to "drug-seeking" at higher rates. Maternal mortality for Black women is 3-4x higher than white women, persisting across ALL education and income levels - a college-educated Black woman has higher maternal mortality risk than a white woman with an 8th-grade education (intersectionality of race and gender). Historical context: Medical experimentation on enslaved Black people (J. Marion Sims), Tuskegee study, forced sterilization contribute to ongoing medical mistrust. Pain is undertreated and often disbelieved, creating barriers to care.

**(2) APPROACH**: "I want to make sure I understand your pain completely and take it seriously. Can you tell me more about what you're experiencing? I'm going to use some tools to help me accurately assess and document your pain so we can get you the right treatment."

**(3) EXPLORE**:
- "Using the Brief Pain Inventory scale, on a scale of 0-10, how would you rate your pain right now, and what's the worst it's been?" [Validated tool reduces implicit bias by standardizing assessment]
- "How does this pain affect your daily activities - work, sleep, relationships, self-care?" [Functional impact assessment provides objective data beyond subjective pain rating]
- "What have you tried so far to manage the pain, and what's worked or not worked?" [Understanding patient's efforts validates their experience and informs treatment]
- "Have you had experiences in the past where you felt your pain wasn't taken seriously?" [Acknowledges potential past trauma and opens discussion about medical mistrust]
- "What concerns do you have about pain treatment?" [Addresses potential concerns about stigma or being labeled "drug-seeking"]

**(4) INTEGRATE**:
- Use Brief Pain Inventory (BPI) or PEG scale (Pain, Enjoyment, General activity) for standardized pain assessment
- Document pain thoroughly in chart with specific quotes from patient and functional impact
- Take "believing stance" - default to believing patient's pain report rather than doubting it
- Provide adequate pain medication at initial visit rather than making patient "prove" pain over multiple visits
- Explain pain treatment plan clearly, including why specific medications chosen
- Schedule follow-up to reassess pain and adjust treatment - demonstrate commitment to pain control
- Be transparent about opioid prescribing when relevant - explain it's about safety, not distrust
- If pain is chronic, consider referral to pain management or multidisciplinary approach

**(5) AVOID**:
- Don't minimize or dismiss pain reports - research shows Black women's pain is systematically underestimated
- Don't attribute pain to "drug-seeking behavior" without clear evidence - this stereotype disproportionately affects Black patients
- Don't make assumptions about pain tolerance based on race - false belief that Black patients have higher pain tolerance
- Don't delay pain treatment while conducting extensive workup - treat pain while investigating cause
- Don't use race-based algorithms or adjustments (e.g., race-corrected eGFR is being phased out due to perpetuating disparities)
- Don't make patient feel they have to "prove" their pain is real

---

## Benefits of Enhanced System

1. **Comprehensive Context Capture**: No aspect of patient's identity or experience is missed
2. **Actionable Guidance**: Doctors receive specific, immediately implementable recommendations
3. **Research-Backed**: All recommendations based on actual research, statistics, and evidence
4. **Culturally Humble**: Acknowledges what doctor might not know and provides education
5. **Intersectional**: Recognizes patients have multiple identities that each deserve attention
6. **Bias Interruption**: Explicitly addresses documented biases and provides counter-strategies
7. **Patient-Centered**: Centers patient's own disclosure and preferences
8. **Scalable**: Works for ANY cultural, religious, ethnic, or identity context

---

## Testing the Enhanced System

To test the enhanced system:

1. **Start backend and frontend** (if not already running):
   ```bash
   ./start.sh
   ```

2. **Select a patient** and click "Begin AI-Assisted Intake"

3. **During the conversation**, when Amani asks the empowerment question, provide a response that mentions multiple dimensions:
   
   Example: "Yes, I'm Muslim and currently fasting for Ramadan, and I'm also gay, and I had a doctor dismiss my pain before."

4. **Review the briefing** - you should see:
   - Multiple separate `equity_and_context_flags` (one for each dimension mentioned)
   - Each flag has comprehensive 5-part recommendation structure
   - Specific, researched information (not generic statements)
   - Concrete, actionable guidance for the doctor

---

## Summary

The enhanced cultural briefing system transforms vague, generic cultural considerations into **comprehensive, researched, actionable guidance** that empowers clinicians to provide excellent culturally informed care. By following the **IDENTIFY → RESEARCH → PROVIDE** framework with the **5-part recommendation structure**, the system ensures that ALL aspects of a patient's identity and experiences are honored and integrated into their care.

