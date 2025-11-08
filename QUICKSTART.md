# Amani Clinical Intake - Quick Start Guide

## Installation (5 minutes)

### Option 1: Automated Setup (Recommended)

```bash
cd /Users/andyliu/Documents/ClaudeHackathon
./setup.sh
```

The script will:
- Check prerequisites (Python, Node.js, PostgreSQL)
- Set up Python virtual environment
- Install all dependencies
- Configure environment variables
- Create and seed database
- Install frontend dependencies

### Option 2: Manual Setup

```bash
# 1. Backend Setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python seed.py

# 2. Frontend Setup
cd ../frontend
npm install
```

## Running the Application

### Easy Start
```bash
./start.sh
```

### Manual Start
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Access Points

- **Application**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/amani_clinic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
ALLOWED_ORIGINS=http://localhost:3000
```

## Quick Demo Flow

1. Open http://localhost:3000
2. Click "Simulate Intake" for patient "Brenda Jones"
3. Select narrative "Fatigue and Foot Numbness"
4. Click "Generate Clinical Briefing"
5. Wait 5-10 seconds for AI processing
6. Click "View Briefing" to see results

## Common Issues

### "Connection refused" error
- Make sure PostgreSQL is running: `brew services start postgresql`
- Check if database exists: `psql -l | grep amani_clinic`

### "API key not valid" error
- Verify your Anthropic API key in `backend/.env`
- Get a key at: https://console.anthropic.com/

### Port already in use
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Kill process on port 3000
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

## Project Overview

This MVP demonstrates AI-powered clinical intake synthesis using:

- **50 synthetic patients** with diverse medical histories
- **Claude 3.5 Sonnet** for intelligent data synthesis
- **FastAPI backend** with PostgreSQL database
- **React frontend** with modern UI

## Key Features

- Patient dashboard with appointment roster
- Multiple narrative scenarios per patient
- Real-time AI synthesis (5-10 seconds)
- Structured clinical briefings with:
  - Clinical summary
  - Risk flags and insights
  - Structured symptoms
  - Relevant medical history

## Next Steps

1. Try different patients and narratives
2. Review the AI-generated briefings
3. Check the code structure in `/backend` and `/frontend`
4. Read the full [README.md](README.md) for detailed documentation

## Support

- Backend logs: `tail -f backend.log`
- Frontend logs: `tail -f frontend.log`
- API documentation: http://localhost:8000/docs

---

For complete documentation, see [README.md](README.md)
