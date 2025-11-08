# Installation Guide

## Prerequisites

Before installing Amani Clinical Intake, ensure you have:

- **Conda** (Anaconda or Miniconda) - [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 12+** - [Download](https://www.postgresql.org/download/)
- **Anthropic API Key** - [Get one](https://console.anthropic.com/)

## Quick Install

```bash
cd /Users/andyliu/Documents/ClaudeHackathon
./setup.sh
```

The automated script will guide you through the setup process.

## Manual Installation

### Step 1: Clone and Navigate

```bash
cd /Users/andyliu/Documents/ClaudeHackathon
```

### Step 2: Set Up PostgreSQL

```bash
# Create the database
createdb amani_clinic

# Or using psql
psql -U postgres
CREATE DATABASE amani_clinic;
\q
```

### Step 3: Backend Setup

```bash
cd backend

# Create conda environment
conda create -n amani python=3.9 -y

# Activate it
conda activate amani

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use any text editor
```

**Required .env variables:**

```env
DATABASE_URL=postgresql://username:password@localhost:5432/amani_clinic
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
ALLOWED_ORIGINS=http://localhost:3000
```

**Get your Anthropic API key:**
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new key
5. Copy and paste into .env

### Step 4: Seed the Database

```bash
# Still in backend directory with conda environment activated
python seed.py
```

You should see:
```
🌱 Starting database seed...
📦 Creating database tables...
✅ Tables created
...
🎉 Database seeding completed successfully!
   • 50 patients loaded
   • 50 EHR histories loaded
   • 50 narratives loaded
```

### Step 5: Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install
```

### Step 6: Verify Installation

```bash
# Terminal 1 - Start backend
cd backend
conda activate amani
uvicorn app.main:app --reload

# Terminal 2 - Start frontend
cd frontend
npm run dev
```

Visit http://localhost:3000 - you should see the patient dashboard.

## Troubleshooting

### PostgreSQL Not Running

**macOS:**
```bash
brew services start postgresql
```

**Linux:**
```bash
sudo systemctl start postgresql
```

**Windows:**
Open Services and start PostgreSQL service

### Database Connection Error

Check your DATABASE_URL in .env:
```bash
# Test connection
psql amani_clinic -c "SELECT 1;"
```

### Python Module Not Found

Make sure conda environment is activated:
```bash
cd backend
conda activate amani
pip list  # Should show installed packages
```

### Node Module Error

Clear and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use

Find and kill the process:
```bash
# Port 8000 (backend)
lsof -i :8000
kill -9 <PID>

# Port 3000 (frontend)
lsof -i :3000
kill -9 <PID>
```

### API Key Invalid

1. Check .env file exists in backend/
2. Verify API key starts with `sk-ant-`
3. Test key at https://console.anthropic.com/
4. Check for extra spaces or quotes

## Verification Checklist

- [ ] Conda installed (`conda --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] PostgreSQL running (`psql -l`)
- [ ] Database `amani_clinic` created
- [ ] Conda environment `amani` created (`conda env list`)
- [ ] Python dependencies installed (`conda activate amani && pip list`)
- [ ] .env file configured with API key
- [ ] Database seeded (50 patients)
- [ ] Frontend dependencies installed
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can access http://localhost:3000

## Next Steps

Once installed:

1. Read [QUICKSTART.md](QUICKSTART.md) for demo walkthrough
2. Try the demo flow with different patients
3. Explore the code structure
4. Read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for technical details

## Support

If you encounter issues not covered here:

1. Check the main [README.md](README.md)
2. Review logs:
   - Backend: Terminal running uvicorn
   - Frontend: Terminal running npm
3. Check API documentation: http://localhost:8000/docs

## Uninstallation

To remove the application:

```bash
# Stop all servers (Ctrl+C)

# Remove conda environment
conda deactivate
conda env remove -n amani

# Remove node modules
rm -rf frontend/node_modules

# Drop database
dropdb amani_clinic

# Remove entire project
rm -rf /Users/andyliu/Documents/ClaudeHackathon
```
