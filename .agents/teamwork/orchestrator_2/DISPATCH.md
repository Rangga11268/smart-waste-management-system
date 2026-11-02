## 2026-11-02T08:43:10Z

Smart Waste Management System (SWMS) for the Bilcode Technology Fullstack Developer Technical Coding Test take-home assessment. Execute Day 2 of the implementation roadmap defined in `docs/TASKS.md`, covering the core FastAPI backend REST API, relational database schema and models, JWT authentication with role-based access control (RBAC), PyTorch ML model integration for waste classification inference, waste reports CRUD with audit logs, admin dashboard stats, API contract verification, and automated backend test suite.

Working directory: D:\Ngoding\interviewWeb\BillcodeTech
Integrity mode: development

## Requirements

### R1. Backend Architecture & Database Connectivity
Initialize the FastAPI application structure in `backend/` with database connectivity supporting PostgreSQL using SQLAlchemy and Alembic, with an automatic local SQLite fallback when PostgreSQL is offline or unreachable so that development and test suites run locally without requiring external services.

### R2. Relational Database Models & Seeding
Implement relational database models (`users`, `categories`, `waste_reports`, `report_logs`) conforming to `docs/ERD.md`, and seed initial categories (`Organic Waste`, `Plastic Waste`, `Paper Waste`) and default test credentials (`admin@bilcode.id` and `user@bilcode.id`) as specified in `docs/RUNBOOK.md`.

### R3. Authentication & Role-Based Access Control
Implement full JWT authentication endpoints (`POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`) with Bcrypt password hashing and role-based access control distinguishing Admin and User roles according to `docs/API_SPECS.md`.

### R4. PyTorch Machine Learning Inference Integration
Integrate the trained PyTorch MobileNetV2 model (`waste_model.pth` via `ml_pipeline/predict.py`) into the `POST /api/v1/predict` endpoint, accepting multipart image uploads and returning predicted category and confidence score.

### R5. Waste Reports Management & Audit Logging
Implement waste report CRUD endpoints (`POST /api/v1/reports`, `GET /api/v1/reports` with keyword search, category and status filters, and pagination, `PATCH /api/v1/reports/{id}/status` restricted to Admin) and record every status transition in `report_logs`.

### R6. Admin Dashboard Statistics Endpoint
Implement the `GET /api/v1/dashboard/stats` endpoint returning aggregate metrics including total reports, counts by status, breakdown by waste category, and active users as defined in `docs/API_SPECS.md`.

### R7. Automated Test Suite & API Contract Verification
Implement a comprehensive pytest automated test suite in `tests/` verifying all endpoints against `docs/API_SPECS.md` (authentication, RBAC permissions, ML inference prediction, reports CRUD, audit logs, and dashboard statistics) using the SQLite database fallback. Interactive OpenAPI documentation must be accessible at `/docs`.

## Acceptance Criteria

### Database & Backend Setup
- [ ] FastAPI application starts and connects successfully to the database (PostgreSQL or local SQLite fallback).
- [ ] Database tables `users`, `categories`, `waste_reports`, and `report_logs` match the schema defined in `docs/ERD.md`.
- [ ] Initial categories (`Organic Waste`, `Plastic Waste`, `Paper Waste`) and seed accounts (`admin@bilcode.id` and `user@bilcode.id`) exist and can authenticate.

### Authentication & Authorization
- [ ] `POST /api/v1/auth/register` creates new user accounts with Bcrypt hashed passwords.
- [ ] `POST /api/v1/auth/login` validates credentials and returns a valid JWT access token.
- [ ] `GET /api/v1/auth/me` returns the authenticated user's profile and role.
- [ ] Admin-only endpoints return HTTP 403 Forbidden when accessed with a non-admin user token.

### Machine Learning Inference
- [ ] `POST /api/v1/predict` accepts image uploads and returns the predicted class (`Organic Waste`, `Plastic Waste`, or `Paper Waste`) and confidence score using `waste_model.pth`.

### Waste Reports & Audit Logging
- [ ] `POST /api/v1/reports` allows authenticated users to submit waste reports with uploaded images, category, description, and geolocation coordinates.
- [ ] `GET /api/v1/reports` supports filtering by status and category, text search, and pagination.
- [ ] `PATCH /api/v1/reports/{id}/status` allows admins to transition report status (`Pending`, `In Progress`, `Completed`, `Rejected`).
- [ ] Every report status change creates a corresponding record in `report_logs` documenting the previous status, new status, changed_by user, and timestamp.

### Admin Dashboard Stats
- [ ] `GET /api/v1/dashboard/stats` returns accurate counts for total reports, reports by status, reports by category, and user counts.

### Verification & Test Suite
- [ ] Automated pytest suite passes cleanly with 0 failures against the SQLite fallback database.
- [ ] Interactive Swagger UI documentation is available at `http://localhost:8000/docs`.
