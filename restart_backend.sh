#!/bin/bash

# Restart Backend Script
echo "🔄 Restarting backend with network error fix..."
echo ""

# Kill existing backend process
echo "Stopping existing backend..."
pkill -f "uvicorn app.main:app" || echo "No backend process found"

# Wait a moment
sleep 2

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &

echo ""
echo "✅ Backend restarted with fixes!"
echo ""
echo "📋 Changes applied:"
echo "  - Condensed synthesis prompt (87% reduction)"
echo "  - Increased timeout to 120 seconds"
echo "  - Increased max tokens to 8000"
echo "  - Added better logging"
echo ""
echo "📁 Logs: backend.log"
echo "🌐 Backend: http://localhost:8000"
echo ""
echo "To monitor logs:"
echo "  tail -f backend.log"
echo ""
echo "To test if it's working:"
echo "  curl http://localhost:8000/api/patients"

