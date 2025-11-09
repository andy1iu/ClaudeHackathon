#!/bin/bash

echo "🔍 Troubleshooting 'Failed to load briefing' issue..."
echo ""

# Check if backend is running
echo "1️⃣ Checking backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend is NOT running on port 8000"
    echo "   Start it with: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
    exit 1
fi

# Test the API endpoint
echo ""
echo "2️⃣ Testing briefing API..."
RESPONSE=$(curl -s -w "%{http_code}" http://localhost:8000/api/patients/SYNTH-001/briefing -o /tmp/briefing_test.json)
if [ "$RESPONSE" = "200" ]; then
    echo "✅ API returns data correctly"
    echo "   Sample: $(cat /tmp/briefing_test.json | head -c 200)..."
else
    echo "❌ API returned error code: $RESPONSE"
    cat /tmp/briefing_test.json
    exit 1
fi

# Check if frontend is running
echo ""
echo "3️⃣ Checking frontend..."
if lsof -i :5173 > /dev/null 2>&1; then
    echo "✅ Frontend appears to be running on port 5173"
elif lsof -i :3000 > /dev/null 2>&1; then
    echo "✅ Frontend appears to be running on port 3000"
else
    echo "⚠️  Frontend might not be running"
    echo "   Start it with: cd frontend && npm run dev"
fi

# Check database
echo ""
echo "4️⃣ Checking database..."
cd backend
source venv/bin/activate
BRIEFING_COUNT=$(python -c "from app.db.database import engine; from sqlalchemy import text; conn = engine.connect(); result = conn.execute(text('SELECT COUNT(*) FROM briefings')); print(result.scalar())")
echo "✅ Found $BRIEFING_COUNT briefings in database"

echo ""
echo "✅ All checks passed!"
echo ""
echo "If you still see 'Failed to load briefing':"
echo "1. Open browser DevTools (F12)"
echo "2. Go to Console tab"
echo "3. Click 'View Clinical Briefing' button"
echo "4. Look for red error messages"
echo "5. Check the Network tab for failed requests"
echo ""
echo "Common fixes:"
echo "- Clear browser cache (Cmd+Shift+R or Ctrl+Shift+R)"
echo "- Restart frontend: cd frontend && npm run dev"
echo "- Check CORS: Make sure backend allows frontend origin"

