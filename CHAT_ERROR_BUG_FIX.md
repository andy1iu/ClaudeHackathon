# Chat Error Bug Fix

## Problem
When the patient sent the message "halal, i can see sounds and hear colors" in response to the empowerment question, the chat showed an error: "Failed to send message. Please try again."

This was happening when the conversation reached the empowerment question and the backend was trying to synthesize the clinical briefing.

## Root Causes Identified

1. **No Timeout Handling**: API calls to Anthropic Claude had no timeout, so if the synthesis took too long, the request would hang or fail
2. **Poor Error Handling**: Errors weren't being logged properly, making debugging difficult
3. **JSON Parsing Issues**: If Claude returned JSON wrapped in markdown code blocks (```json ... ```), the parser would fail
4. **No Error Recovery**: When a message failed to send, the user message stayed in the UI with no way to retry

## Fixes Applied

### Backend Fixes (`backend/app/api/chat.py`)

#### 1. Added Timeouts
- **Chat responses**: 30 second timeout
- **Synthesis (briefing generation)**: 60 second timeout

```python
# Chat timeout
response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=500,
    temperature=0.7,
    timeout=30.0,  # NEW: 30 second timeout
    system=system_prompt,
    messages=api_messages
)

# Synthesis timeout
message = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=4000,
    temperature=0.3,
    timeout=60.0,  # NEW: 60 second timeout
    messages=[{"role": "user", "content": synthesis_prompt}]
)
```

#### 2. Better JSON Parsing
Added cleanup to handle cases where Claude returns JSON wrapped in markdown:

```python
# Clean up response text (remove any markdown code blocks if present)
response_text = response_text.strip()
if response_text.startswith("```json"):
    response_text = response_text[7:]  # Remove ```json
if response_text.startswith("```"):
    response_text = response_text[3:]  # Remove ```
if response_text.endswith("```"):
    response_text = response_text[:-3]  # Remove trailing ```
response_text = response_text.strip()
```

#### 3. Better Error Logging
Added detailed logging to help diagnose issues:

```python
except json.JSONDecodeError as json_err:
    # Log the problematic response for debugging
    print(f"Failed to parse JSON response: {response_text[:500]}")
    raise HTTPException(
        status_code=500,
        detail=f"AI returned invalid JSON format. Please try again."
    )
```

#### 4. Defensive Field Access
Changed from direct field access to `.get()` with defaults:

```python
# Before: briefing_data["ai_summary"]
# After: briefing_data.get("ai_summary", "Summary not available")

ai_summary=briefing_data.get("ai_summary", "Summary not available"),
key_insights_flags=briefing_data.get("key_insights_flags", []),
equity_and_context_flags=briefing_data.get("equity_and_context_flags", []),
reported_symptoms_structured=briefing_data.get("reported_symptoms_structured", []),
relevant_history_surfaced=briefing_data.get("relevant_history_surfaced", [])
```

### Frontend Fixes (`frontend/src/components/IntakeChatModal.jsx`)

#### 1. Better Error Messages
Show the actual error message from the backend instead of generic message:

```javascript
catch (err) {
  console.error('Failed to send message:', err);
  console.error('Error details:', err.response?.data);
  
  // Show more detailed error message
  const errorMessage = err.response?.data?.detail || err.message || 'Failed to send message. Please try again.';
  setError(errorMessage);
  
  // Remove the user message from UI since it failed
  setMessages(prev => prev.slice(0, -1));
}
```

#### 2. Remove Failed Messages
When a message fails to send, it's now removed from the UI so the user can try again without confusion.

## How to Apply the Fix

### Option 1: Restart Backend Only
```bash
./restart_backend.sh
```

### Option 2: Restart Everything
```bash
./start.sh
```

### Option 3: Manual Restart
```bash
# Stop backend
pkill -f "uvicorn app.main:app"

# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The frontend will automatically pick up the changes (if running with Vite dev server).

## Testing the Fix

1. **Restart the backend** using one of the methods above
2. **Start a new intake conversation** with any patient
3. **When asked the empowerment question**, try providing a complex response like:
   - "I'm Muslim and currently fasting for Ramadan"
   - "I'm Buddhist and I'm gay and had a bad experience"
   - "halal, i can see sounds and hear colors"
4. **The message should now send successfully** and the briefing should be generated

## What to Check

- ✅ Error messages are now more descriptive
- ✅ Failed messages are removed from UI so you can retry
- ✅ Timeouts prevent hanging requests
- ✅ JSON parsing is more robust
- ✅ Backend logs show detailed error information for debugging

## If Issues Persist

1. **Check backend logs**:
   ```bash
   tail -f backend.log
   ```

2. **Check browser console** (F12 → Console tab) for detailed error messages

3. **Check if backend is running**:
   ```bash
   curl http://localhost:8000/api/patients
   ```

4. **Check Anthropic API key** is valid:
   ```bash
   cd backend
   source venv/bin/activate
   python -c "from app.core.config import settings; print('API Key:', settings.ANTHROPIC_API_KEY[:20] + '...')"
   ```

## Additional Improvements Made

- More robust error handling throughout the chat flow
- Better logging for debugging synthesis issues
- Graceful degradation when optional fields are missing
- Timeout protection against hanging API calls

## Summary

The bug was caused by a combination of:
1. No timeout handling on API calls
2. Poor error handling and logging
3. Fragile JSON parsing
4. No user feedback on failures

All of these have been addressed with the fixes above. The chat should now handle errors gracefully and provide better feedback to users when issues occur.

