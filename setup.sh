#!/bin/bash

# Amani Clinical Intake - Setup Script
# This script automates the initial setup process

echo "========================================="
echo "Amani Clinical Intake - Setup Wizard"
echo "========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ Python $PYTHON_VERSION found"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
else
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION found"
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL 12 or higher."
    exit 1
else
    PSQL_VERSION=$(psql --version | cut -d' ' -f3)
    echo "✅ PostgreSQL $PSQL_VERSION found"
fi

echo ""
echo "========================================="
echo "Setting up Backend"
echo "========================================="
echo ""

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Python dependencies installed"

# Setup .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Setting up environment variables..."
    cp .env.example .env
    echo ""
    echo "❗ IMPORTANT: You need to configure your .env file"
    echo ""
    echo "Please provide the following information:"
    echo ""

    # Get database info
    read -p "PostgreSQL username (default: $USER): " DB_USER
    DB_USER=${DB_USER:-$USER}

    read -sp "PostgreSQL password (press enter if none): " DB_PASS
    echo ""

    read -p "Database name (default: amani_clinic): " DB_NAME
    DB_NAME=${DB_NAME:-amani_clinic}

    # Get Anthropic API key
    echo ""
    read -p "Anthropic API Key (from https://console.anthropic.com/): " API_KEY
    echo ""

    # Update .env file
    if [ -z "$DB_PASS" ]; then
        DB_URL="postgresql://$DB_USER@localhost:5432/$DB_NAME"
    else
        DB_URL="postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME"
    fi

    cat > .env << EOF
DATABASE_URL=$DB_URL
ANTHROPIC_API_KEY=$API_KEY
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
EOF

    echo "✅ Environment variables configured"
else
    echo "✅ .env file already exists"
fi

# Create database if it doesn't exist
echo ""
echo "📊 Setting up database..."
if psql -lqt | cut -d \| -f 1 | grep -qw amani_clinic; then
    echo "✅ Database 'amani_clinic' already exists"
else
    echo "Creating database 'amani_clinic'..."
    createdb amani_clinic 2>/dev/null || psql -c "CREATE DATABASE amani_clinic;"
    echo "✅ Database created"
fi

# Seed database
echo ""
echo "🌱 Seeding database with synthetic data..."
python seed.py
echo ""

cd ..

echo ""
echo "========================================="
echo "Setting up Frontend"
echo "========================================="
echo ""

cd frontend

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install
echo "✅ Node.js dependencies installed"

cd ..

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "🎉 Amani Clinical Intake is ready to use!"
echo ""
echo "To start the application, run:"
echo "  ./start.sh"
echo ""
echo "Or start servers manually:"
echo "  Terminal 1: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
echo "📚 Read README.md for more information"
echo ""
