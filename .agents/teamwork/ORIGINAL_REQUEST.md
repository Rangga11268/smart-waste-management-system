# Original User Request

## Approved Task Prompt — 2026-11-01T12:07:11Z

Smart Waste Management System (SWMS) for the Bilcode Technology Fullstack Developer Technical Coding Test take-home assessment. Execute Day 1 of the implementation roadmap defined in `docs/TASKS.md`, covering monorepo setup, ML dataset curation, PyTorch MobileNetV2 transfer learning, evaluation metrics, and model export.

Working directory: D:\Ngoding\interviewWeb\BillcodeTech
Integrity mode: development

## Requirements

### R1. Monorepo Project Structure Setup
Establish the project directory structure with modules for `backend`, `ml_pipeline`, `web`, `mobile`, and `docs` as defined in `docs/TASKS.md` (Task 1.1).

### R2. Dataset Collection & Curation
Download and curate a dataset of at least 150 images across three categories: Organic Waste, Plastic Waste, and Paper Waste (minimum 50 images per category) from public sources. Organize the dataset with an 80% training and 20% validation/testing split, and document data source citations.

### R3. Machine Learning Training Pipeline
Implement a PyTorch transfer learning training script using MobileNetV2 (`ml_pipeline/train.py` or equivalent) with image data augmentation. The training pipeline must achieve an evaluation accuracy of at least 80% (target >= 85%) on the test/validation set.

### R4. Evaluation Artifacts & Model Export
Export the trained model weights to `waste_model.pth`. Generate evaluation outputs including a confusion matrix plot (`confusion_matrix.png`), training loss and accuracy curves (`accuracy_curve.png`), and a text classification report (`classification_report.txt`) showing precision, recall, and F1-score for each class.

### R5. Adherence to Technical Specifications
Follow the specifications, architecture guidelines, and standards outlined in `docs/` (`PRD.md`, `SPEC.md`, `ARCHITECTURE.md`, `ADR.md`, `RUNBOOK.md`, `TASKS.md`).

## Acceptance Criteria

### Project Structure
- [ ] Monorepo directories (`backend/`, `ml_pipeline/`, `web/`, `mobile/`, `docs/`) exist in `D:\Ngoding\interviewWeb\BillcodeTech`.

### Dataset
- [ ] Dataset contains at least 150 total images with at least 50 images for each class (`organic`, `plastic`, `paper`).
- [ ] Dataset is organized into an 80/20 train and validation/test partition.
- [ ] Dataset sources are documented with citations.

### Training & Model
- [ ] Training script executes without error using PyTorch and MobileNetV2 architecture.
- [ ] Model weights file `waste_model.pth` is exported and loadable for inference.

### Metrics & Evaluation
- [ ] Test/validation accuracy is >= 80%.
- [ ] `confusion_matrix.png` is generated and displays classification performance across all 3 categories.
- [ ] `accuracy_curve.png` (or loss/accuracy curves) is generated and saved.
- [ ] `classification_report.txt` contains precision, recall, and F1-score for each category.


## Approved Task Prompt (Day 2) — 2026-11-02T08:41:35Z

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


## Approved Task Prompt (Day 3) — 2026-11-02T12:30:41Z

Smart Waste Management System (SWMS) Web Dashboard (Admin & User) for the Bilcode Technology Fullstack Developer Technical Coding Test take-home assessment, implementing Day 3 of the roadmap in Next.js 14 App Router and Tailwind CSS.

Working directory: D:\Ngoding\interviewWeb\BillcodeTech
Integrity mode: development

## Requirements

### R1. Next.js 14 App Router Setup & Eco-Tech Design System
Setup the Next.js 14 web application in `web/` configured with Tailwind CSS and Lucide icons, adhering to the Eco-Tech styling guide in `docs/STYLING_GUIDE.md`: Space Grotesk for headings/display, Inter for body/forms/tables, JetBrains Mono for GPS coordinates and report IDs, and emerald primary `#059669` with semantic status badges (amber for Pending, blue for In Progress, emerald for Completed, rose for Rejected).

### R2. Authentication, Session Management & Route Protection
Implement the login page and session management integrated with backend `POST /api/v1/auth/login`, storing JWT access tokens, handling auth state, and enforcing role-based route protection where users with the Admin role are granted access to Dashboard, Reports Management, and User Management.

### R3. Analytics Dashboard
Implement the `/dashboard` page displaying key statistics fetched from `GET /api/v1/dashboard/stats`, including 4 primary metric cards (Total Reports, Pending Verification, In Progress, Completion Rate %), waste category distribution visualization (Organic, Plastic, Paper), and recent activity logs.

### R4. Waste Reports Management Table & Review Modal
Implement the `/reports` page with keyword text search (title, description, location benchmark), status and category filter dropdowns, pagination, and colored semantic status badges. Implement a report review modal featuring uploaded photo preview, AI detection badge (detected category and confidence score), GPS coordinates with a direct Google Maps link (`https://www.google.com/maps?q=lat,long`), and an admin status update action form (`PATCH /api/v1/reports/{id}/status`) with disposition notes (`admin_notes`).

### R5. User Management & API Client
Implement the API client in `web/src/lib/api.ts` configured with `NEXT_PUBLIC_API_URL` (connecting to `http://localhost:8000`) and automatic Bearer token injection, current user profile display from `GET /api/v1/auth/me`, and user management list view for administrators.

### R6. Verification & Responsive Build
Ensure all pages and components have responsive layouts across mobile, tablet, and desktop viewports, with a successful Next.js production build (`npm run build`), TypeScript type checking, and linting passing with zero errors in `web/`.

## Acceptance Criteria

### Design System & Layout
- [ ] Space Grotesk is configured for Headings/Display, Inter for Body/Forms/Tables, and JetBrains Mono for GPS coordinates and report IDs per `docs/STYLING_GUIDE.md`.
- [ ] Eco-Tech color palette is applied with emerald primary `#059669` and semantic badges (Pending: amber, In Progress: blue, Completed: emerald, Rejected: rose).
- [ ] Layout renders responsively across mobile, tablet, and desktop viewports without horizontal scroll overflow.

### Authentication & RBAC
- [ ] Login form submits credentials to `POST /api/v1/auth/login` and persists the returned JWT token.
- [ ] Unauthenticated requests to protected routes redirect to the login page.
- [ ] Protected admin routes restrict access to authenticated users with the Admin role.

### Dashboard & Analytics
- [ ] `/dashboard` fetches aggregate metrics from `GET /api/v1/dashboard/stats`.
- [ ] 4 metric cards display correct data for Total Reports, Pending, In Progress, and Completion Rate %.
- [ ] Category distribution breakdown (Organic, Plastic, Paper) and recent activity logs are rendered.

### Reports Management & Review Modal
- [ ] `/reports` displays reports table populated from `GET /api/v1/reports`.
- [ ] Keyword text search, status dropdown filter, and category dropdown filter update displayed reports.
- [ ] Pagination controls navigate across multiple pages of report records.
- [ ] Review modal displays report image, AI classification category with confidence percentage, GPS coordinates, and clickable Google Maps link.
- [ ] Admin disposition form executes `PATCH /api/v1/reports/{id}/status` with selected status and `admin_notes`, updating the report state.

### User Management & API Client
- [ ] `web/src/lib/api.ts` connects via `NEXT_PUBLIC_API_URL` and attaches Bearer authorization header to authenticated requests.
- [ ] Authenticated user profile information displays data from `GET /api/v1/auth/me`.
- [ ] User management view displays registered users for admin accounts.

### Build & Verification
- [ ] `npm run build` inside `web/` completes successfully with zero compilation or lint errors.
