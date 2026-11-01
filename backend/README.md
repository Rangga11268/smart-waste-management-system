# SWMS Core Backend Service

FastAPI-powered RESTful API gateway and AI inference microservice for the Smart Waste Management System (SWMS).

---

## Features

- **High-Performance Async REST API**: Built on FastAPI and Uvicorn.
- **In-Memory ML Inference**: Loads trained PyTorch MobileNetV2 weights (`waste_model.pth`) directly into application memory on startup for sub-800ms image classification.
- **JWT RBAC Authentication**: Secure token-based access with role differentiation between citizens (`user`) and sanitation operators (`admin`).
- **PostgreSQL Persistence**: ACID-compliant transactional persistence using SQLAlchemy 2.0 ORM with Alembic schema migrations and an immutable audit trail (`report_logs`).
- **Interactive Documentation**: Auto-generated OpenAPI 3.0 documentation via Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## Directory Structure

```
backend/
├── app/
│   ├── api/v1/           # Versioned API routes (auth, predict, reports, users)
│   ├── core/             # Configuration, security (JWT/bcrypt), database session
│   ├── models/           # SQLAlchemy ORM models (User, WasteReport, Category, ReportLog)
│   ├── schemas/          # Pydantic schemas for request validation & response serialization
│   ├── services/         # Business logic & PyTorch model loader
│   ├── __init__.py
│   └── main.py           # Application entrypoint & CORS middleware
├── uploads/              # Local storage for evidence photos (.gitkeep)
├── tests/                # Automated pytest unit & integration tests
├── requirements.txt      # Python dependencies
└── README.md             # This guide
```

---

## Local Setup

### 1. Create Virtual Environment
```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the `backend/` directory:
```env
PROJECT_NAME="Smart Waste Management System"
VERSION="1.0.0"
API_V1_STR="/api/v1"

# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/swms_db"

# Security
JWT_SECRET="replace-with-a-secure-random-secret-key-min-32-chars"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Static Storage
UPLOAD_DIR="./uploads"
```

### 4. Run Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Once started, access:
- Healthcheck: `http://localhost:8000/health`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Automated Testing

```bash
pytest tests/ -v --cov=app
```

---

## Day 2 Implementation Roadmap

- **Auth Module**: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- **AI Inference Endpoint**: `POST /api/v1/predict` (multipart image upload $\rightarrow$ PyTorch inference $\rightarrow$ category + confidence score)
- **Reports CRUD**: `POST /api/v1/reports`, `GET /api/v1/reports`, `PATCH /api/v1/reports/{id}/status`
- **Audit Logging**: Automatic append to `report_logs` on any status update
