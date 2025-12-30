#!/bin/bash

# Tarento Complaint Tracker - Quick Start Script

echo "🚀 Starting Tarento Complaint Tracker..."

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  backend/.env not found! Copying from example..."
    cp backend/.env.example backend/.env
    echo "❗ Please edit backend/.env and add your GEMINI_API_KEY"
fi

# Option to run with Docker
if [ "$1" == "docker" ]; then
    echo "🐳 Running with Docker Compose..."
    docker-compose up --build
    exit 0
fi

# Local setup
echo "💻 Setting up locally..."

# Backend
echo "📦 Installing Backend Dependencies..."
cd backend
pip install -r requirements.txt > /dev/null

echo "🌱 Seeding Database..."
python scripts/seed_data.py

echo "🔥 Starting Backend Server (Background)..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
echo "🎨 Installing Frontend Dependencies..."
cd ../frontend
npm install > /dev/null

echo "✨ Starting Frontend..."
npm run dev &
FRONTEND_PID=$!

echo "✅ App is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend: http://localhost:8000"
echo "   Admin Login: admin@tarento.com / admin123"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
