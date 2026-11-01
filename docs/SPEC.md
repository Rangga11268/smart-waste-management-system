# Technical Specification: Smart Waste Management System (SWMS)

> **Gated Spec — Spec-Driven Development Standard**
> Repository: `BillcodeTech` (Monorepo)  
> Target: Take-Home Coding Test Fullstack Developer — Bilcode Technology

---

## Assumptions Made
1. **Unified Backend**: FastAPI handles both the business logic (Auth, Reports CRUD, User Management) and the ML image classification inference (`/api/v1/predict`) to avoid managing two separate backend servers.
2. **Cloud Database**: PostgreSQL hosted on Supabase or Neon (free tier, no local installation barrier for evaluators).
3. **Web Client**: Next.js 14+ (App Router) + Tailwind CSS + Lucide Icons deployed to Vercel for instant live preview.
4. **Mobile Client**: Flutter targeting Android (compiled to a release `.apk` for direct evaluator installation).
5. **ML Strategy**: Transfer Learning with MobileNetV2 (PyTorch) trained on at least 150 curated images across 3 classes: *Organic Waste*, *Plastic Waste*, and *Paper Waste*.

---

## 1. Objective
Build an end-to-end Smart Waste Management System enabling citizens to report waste piles with AI-assisted classification and automated GPS geotagging, while municipal sanitation operators manage, filter, and track reports through an interactive web dashboard.

### Core Goals:
- **ML Component (20%)**: High accuracy ($\ge 80\%$) waste image classification model with full evaluation artifacts (Confusion Matrix, Loss/Acc curves, Classification Report).
- **Backend Component (15%)**: Robust FastAPI service with JWT RBAC (Admin & User), multipart image upload, and automated Swagger UI (`/docs`).
- **Web Dashboard (25%)**: Responsive Next.js application with interactive charts, filterable CRUD table, and report status updater.
- **Mobile App (20%)**: Native-feeling Flutter app with Camera integration, GPS acquisition (`geolocator`), and direct inference consumption.
- **Deliverables & Docs (20%)**: Comprehensive README, ERD, API Specs, Styling Guide, release APK, and a $\le 10$-minute demo video.

---

## 2. Executable Commands

### A. Machine Learning Pipeline (`ml_pipeline/`)
```bash
# Setup virtualenv
python -m venv venv
venv\Scripts\activate

# Install ML dependencies
pip install torch torchvision torchaudio scikit-learn matplotlib seaborn pillow numpy

# Run training (with data augmentation & transfer learning)
python train.py --epochs 15 --batch-size 16 --data-dir ./dataset

# Run evaluation & generate metrics artifacts
python evaluate.py --model ./saved_models/waste_model.pth --test-dir ./dataset/test
```

### B. Backend API (`backend/`)
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Run local development server (with hot reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run automated tests
pytest tests/ -v --cov=app
```

### C. Web Frontend (`web/`)
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build production bundle
npm run build

# Start production server
npm run start
```

### D. Mobile Application (`mobile/`)
```bash
# Get Flutter dependencies
flutter pub get

# Run on connected device / emulator
flutter run

# Build standalone Android Release APK
flutter build apk --release
```

---

## 3. Project Structure

```text
BillcodeTech/
├── backend/                  # FastAPI Core Backend + ML Inference Service
│   ├── app/
│   │   ├── api/v1/           # Modular routers: auth, reports, users, predict
│   │   ├── core/             # Config, security (JWT), database session
│   │   ├── models/           # SQLAlchemy ORM models (User, Report, Category, Log)
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic & PyTorch model loader
│   │   └── main.py           # Application entrypoint & CORS
│   ├── uploads/              # Static media uploads (evidence photos)
│   ├── tests/                # Pytest unit & integration test suite
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile
│
├── ml_pipeline/              # Machine Learning Training & Evaluation
│   ├── dataset/              # 150+ images (organic, plastic, paper)
│   ├── train.py              # PyTorch MobileNetV2 Training Script
│   ├── evaluate.py           # Metrics generator (confusion matrix, report)
│   └── saved_models/         # Exported weights (waste_model.pth)
│
├── web/                      # Admin & User Web Dashboard (Next.js 14+)
│   ├── src/
│   │   ├── app/              # App Router (dashboard, reports, users, login)
│   │   ├── components/       # UI Components (Sidebar, StatCard, ReportModal, Table)
│   │   └── lib/              # Axios instance, token storage, utils
│   ├── package.json
│   └── tailwind.config.ts
│
├── mobile/                   # Flutter Mobile App
│   ├── lib/
│   │   ├── models/           # Dart data models
│   │   ├── screens/          # Login, Register, Home, CreateReport, History
│   │   ├── services/         # API Service (Camera, GPS, HTTP client)
│   │   └── main.dart
│   └── pubspec.yaml
│
└── docs/                     # Documentation & Deliverables
    ├── PRD.md                # Product Requirements Document
    ├── SPEC.md               # Technical Specification (This File)
    ├── STYLING_GUIDE.md      # Design tokens, palette & UI guidelines
    ├── ERD.md                # Entity Relationship Diagram & DB Schema
    ├── API_SPECS.md          # OpenAPI / REST API Contracts
    └── TASKS.md              # 5-Day Implementation Roadmap
```

---

## 4. Code Style & Architecture Examples

### A. Python / FastAPI (Clean Separation & Type Safety)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.report import ReportResponse, ReportStatusUpdate
from app.services.report_service import update_report_status
from app.core.security import get_current_admin_user

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.patch("/{report_id}/status", response_model=ReportResponse)
def update_status(
    report_id: str,
    payload: ReportStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)
):
    """Admin-only endpoint to update waste report workflow status."""
    report = update_report_status(db, report_id, payload.status, payload.admin_notes, admin.id)
    if not report:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    return report
```

### B. Next.js React Component (Clean & Accessible)
```tsx
import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, XCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: 'Pending' | 'In Progress' | 'Completed' | 'Rejected';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const badgeStyles = {
    'Pending': 'bg-amber-50 text-amber-700 border-amber-200',
    'In Progress': 'bg-blue-50 text-blue-700 border-blue-200',
    'Completed': 'bg-emerald-50 text-emerald-700 border-emerald-200',
    'Rejected': 'bg-rose-50 text-rose-700 border-rose-200',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full border ${badgeStyles[status]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
};
```

---

## 5. Testing Strategy

1. **Backend Testing**:
   * Framework: `pytest` + `httpx.AsyncClient`.
   * Location: `backend/tests/`.
   * Scope: Auth validation (login/register), role guards (user vs admin), and report submission.
2. **ML Evaluation**:
   * Metric targets:
     * Overall accuracy $\ge 80\%$ on held-out testing set ($20\%$).
     * Confusion matrix saved to `ml_pipeline/artifacts/confusion_matrix.png`.
     * Detailed classification report (Precision, Recall, F1 per class) saved to `ml_pipeline/artifacts/classification_report.txt`.
3. **Manual Verification**:
   * End-to-end test: Ambil foto dari Flutter $\rightarrow$ kirim ke `/predict` $\rightarrow$ periksa label kategori $\rightarrow$ submit laporan $\rightarrow$ buka Web Admin $\rightarrow$ verifikasi laporan muncul di tabel dan marker peta $\rightarrow$ update status ke `Completed`.

---

## 6. Boundaries

- **Always Do**:
  - Validasi schema request dengan Pydantic di Backend dan form validation di Frontend/Mobile.
  - Berikan feedback visual (loading indicator, toast error/success) saat proses upload foto dan inferensi AI.
  - Catat log perubahan status laporan ke tabel `report_logs` untuk audit trail.
- **Ask First**:
  - Menambah kategori baru di luar 3 kategori wajib (*Organic*, *Plastic*, *Paper*).
  - Mengubah arsitektur cloud hosting atau menambahkan dependency berbayar.
- **Never Do**:
  - Hardcode secret key / database password di repositori publik (selalu gunakan `.env`).
  - Mengunggah file dataset berukuran ratusan megabyte langsung ke git tracking tanpa `.gitignore` atau Git LFS.
  - Membuat UI yang menggunakan emoji berantakan di heading sistem enterprise.

---

## 7. Success Criteria

| ID | Criteria | Target | Verification Method |
| :--- | :--- | :--- | :--- |
| **SC-01** | Model Testing Accuracy | $\ge 80\%$ | `python evaluate.py` classification report |
| **SC-02** | AI Inference Latency | $< 800$ ms | API response header / network tab |
| **SC-03** | Auth & RBAC Security | 100% Guarded | Unauthorized requests return `401`/`403` |
| **SC-04** | Web Responsiveness | Mobile, Tablet, Desktop | Chrome DevTools device mode test |
| **SC-05** | Standalone APK Output | Valid `.apk` binary | Installs & runs cleanly on Android test device |
| **SC-06** | 10 Deliverables Checklist | 10/10 Fulfilled | Validated against email brief checklist |
