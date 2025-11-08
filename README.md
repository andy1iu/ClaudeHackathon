# Amani Clinical Intake - Virtual Clinic MVP

A demonstration application showcasing how AI-powered synthesis of patient narratives with historical medical data can provide clinicians with game-changing pre-appointment insights.

## Overview

This MVP creates a "Virtual Clinic" that simulates the complete Amani Clinical Intake workflow:
1. Clinician views patient roster
2. Selects a patient and their intake narrative
3. AI synthesizes narrative with EHR data using Claude API
4. Generates a structured Clinical Briefing for clinician review

## Tech Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy, PostgreSQL
- **AI Engine**: Anthropic Claude API (Claude 3.5 Sonnet)
- **Frontend**: React 18, Vite, Axios
- **Database**: PostgreSQL

## Project Structure

```
ClaudeHackathon/
├── backend/
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   ├── core/          # Configuration
│   │   ├── db/            # Database connection
│   │   ├── models/        # SQLAlchemy models
│   │   └── schemas/       # Pydantic schemas
│   ├── data/              # Synthetic data JSON files
│   ├── seed.py            # Database seeding script
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service layer
│   │   ├── App.jsx        # Main app component
│   │   └── main.jsx       # Entry point
│   └── package.json       # Node dependencies
└── README.md
```

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- PostgreSQL 12 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Setup Instructions

### 1. Database Setup

Install PostgreSQL if you haven't already, then create the database:

```bash
# macOS (using Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb amani_clinic

# Or using psql
psql postgres
CREATE DATABASE amani_clinic;
\q
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your credentials:
# DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/amani_clinic
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# ALLOWED_ORIGINS=http://localhost:3000

# Seed the database with synthetic data
python seed.py
```

You should see output confirming 50 patients, 50 EHR records, and 50 narratives were loaded.

### 3. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# The frontend is configured to proxy API requests to localhost:8000
```

### 4. Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`

## Usage Guide

### Demo Flow

1. **Dashboard View**: The application loads showing 50 synthetic patients with "Pending Intake" status

2. **Simulate Intake**:
   - Click "Simulate Intake" button for any patient
   - A modal opens showing available patient narratives
   - Select a narrative (e.g., "Fatigue and Foot Numbness")
   - Click "Generate Clinical Briefing"

3. **AI Processing**:
   - The system sends patient data + narrative to Claude API
   - Claude analyzes and synthesizes the information (~5-10 seconds)
   - A structured Clinical Briefing is generated and saved

4. **View Briefing**:
   - Patient status updates to "Briefing Ready"
   - Click "View Briefing" to see the results
   - The briefing includes:
     - Clinical Summary
     - Key Insights & Risk Flags
     - Structured Symptom Documentation
     - Relevant Medical History

### Key Features Demonstrated

- **Data Synthesis**: AI connects patient narratives with EHR history
- **Risk Identification**: Flags potential complications (e.g., diabetic neuropathy, medication adherence issues)
- **Clinical Efficiency**: Pre-appointment preparation reduces appointment time
- **Structured Output**: Consistent, well-organized clinical documentation

## API Endpoints

### Patients
- `GET /api/patients` - List all patients with briefing status
- `GET /api/patients/{patient_id}/narratives` - Get narratives for a patient
- `GET /api/patients/{patient_id}/briefing` - Get clinical briefing for a patient

### Synthesis
- `POST /api/synthesize` - Generate clinical briefing
  ```json
  {
    "patient_id": "SYNTH-001",
    "narrative": "Patient's narrative text..."
  }
  ```

### Health
- `GET /` - API information
- `GET /health` - Health check

## Synthetic Data

The application includes 50 synthetic patients with diverse:
- Medical conditions (diabetes, hypertension, asthma, autoimmune diseases, etc.)
- Demographics (age, gender, race)
- Medication regimens
- Recent lab results
- Patient narratives describing current concerns

All data is completely synthetic and HIPAA-compliant for demonstration purposes.

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# Verify database exists
psql -l | grep amani_clinic

# Test connection
psql amani_clinic -c "SELECT 1;"
```

### Backend Issues
```bash
# Check if port 8000 is available
lsof -i :8000

# View backend logs
# Errors will be shown in the terminal running uvicorn

# Re-seed database if needed
python seed.py
```

### Frontend Issues
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 3000 is available
lsof -i :3000
```

### API Key Issues
- Verify your Anthropic API key is valid
- Check that `.env` file exists and is properly formatted
- Ensure you have credits remaining in your Anthropic account
- API key should start with `sk-ant-`

## Development Notes

### Adding More Synthetic Patients
Edit the JSON files in `backend/data/`:
- `patients.json` - Patient demographics
- `ehr.json` - Medical history, medications, labs
- `narratives.json` - Patient intake narratives

Then re-run: `python seed.py`

### Customizing the AI Prompt
Edit `backend/app/api/synthesize.py`, function `build_synthesis_prompt()`

### Styling Changes
Edit `frontend/src/App.css`

## Security Notes

- Never commit `.env` files
- Keep API keys secure
- This is a demo application - additional security hardening needed for production
- Database credentials should use environment variables in production

## License

This is a demonstration project for the Claude Hackathon.

## Support

For issues or questions, please refer to the troubleshooting section or check:
- FastAPI docs: https://fastapi.tiangolo.com/
- Anthropic Claude API: https://docs.anthropic.com/
- React docs: https://react.dev/

---

Built with Claude Code for the Anthropic Hackathon
