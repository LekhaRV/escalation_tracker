# Tarento AI Complaint Tracking System

A production-ready, AI-powered complaint tracking and management system built for Tarento Technologies. Features intelligent routing, organization-wide visibility, and executive insights using Google Gemini AI.

## Features

- **Multi-Tenant Architecture**: Supports multiple organizations with secure data isolation.
- **AI-Powered Categorization**: Automatically categorizes complaints using Google Gemini.
- **Intelligent Routing**: Assigns complaints to the best-suited project team member based on skills and workload.
- **SLA Monitoring**: Auto-escalates issues that breach service level agreements.
- **Executive Insights**: Generates weekly AI summaries and pattern detection.
- **Real-time Dashboard**: Interactive analytics and reporting.

## Tech Stack

- **Backend**: FastAPI (Python), SQLAlchemy (Async), PostgreSQL, Redis
- **Frontend**: React, Vite, TailwindCSS, Recharts
- **AI**: Google Gemini Pro
- **Infrastructure**: Docker, Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.10+ (for local backend dev)

### Setup & Run

1. **Clone and Configure**
   ```bash
   # Copy environment file
   cp backend/.env.example backend/.env
   # Edit backend/.env with your Gemini API Key
   ```

2. **Run with Docker (Recommended)**
   ```bash
   docker-compose up --build
   ```

3. **Run Locally**

   **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   # Initialize DB and Seed Data
   python scripts/seed_data.py
   # Run Server
   uvicorn app.main:app --reload
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the App**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/api/v1/docs

## Default Credentials (Seed Data)

- **Admin**: `admin@tarento.com` / `admin123`
- **Manager**: `manager@tarento.com` / `manager123`
- **Developer**: `dev1@tarento.com` / `dev123`

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── agents/      # AIAgents (Parser, Categorizer, etc.)
│   │   ├── api/         # API Endpoints
│   │   ├── core/        # Config, Security, Logging
│   │   ├── models/      # Database Models
│   │   ├── services/    # Business Logic
│   │   └── main.py      # App Entry
│   └── scripts/         # Utilities (Seeding)
└── frontend/
    ├── src/
    │   ├── components/  # UI Components
    │   ├── pages/       # Route Pages
    │   └── services/    # API Clients
```

## AI Agents

- **EmailParser**: Runs every 5 mins to ingest emails via IMAP.
- **Categorization**: Runs every 2 mins to classify new complaints.
- **Mapping**: Runs every 3 mins to route complaints to team members.
- **Escalation**: Runs hourly to check SLA breaches.
- **Pattern**: Runs daily to detect recurring issues.
- **Insight**: Runs weekly to generate executive reports.
