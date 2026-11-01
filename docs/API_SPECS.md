# API Contract & Specifications
## Smart Waste Management System (SWMS)

> **Base URL (Local):** `http://localhost:8000/api/v1`  
> **Interactive Documentation:** `http://localhost:8000/docs` (Swagger UI)  
> **OpenAPI JSON Spec:** `http://localhost:8000/openapi.json`

---

## 1. Authentication & User Management

### `POST /auth/register`
Mendaftarkan akun warga/user baru.
* **Auth:** Public
* **Request Body (`application/json`):**
  ```json
  {
    "full_name": "Darell Rangga",
    "email": "user@example.com",
    "password": "Password123!",
    "phone_number": "08123456789"
  }
  ```
* **Response `201 Created`:**
  ```json
  {
    "status": "success",
    "message": "User registered successfully",
    "data": {
      "id": "7c8e9b81-64d4-482a-bc91-2489e24f4692",
      "email": "user@example.com",
      "full_name": "Darell Rangga",
      "role": "user"
    }
  }
  ```

---

### `POST /auth/login`
Autentikasi akun dan generate access token.
* **Auth:** Public
* **Request Body (`application/json` atau `x-www-form-urlencoded`):**
  ```json
  {
    "email": "admin@bilcode.id",
    "password": "SecretAdminPassword!"
  }
  ```
* **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "user": {
        "id": "993a401c-3b09-4bf9-8ebf-cfce48375422",
        "email": "admin@bilcode.id",
        "full_name": "Super Admin",
        "role": "admin"
      }
    }
  }
  ```

---

### `GET /auth/me`
Mendapatkan profil pengguna yang sedang login saat ini.
* **Auth:** `Bearer <token>`
* **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "data": {
      "id": "993a401c-3b09-4bf9-8ebf-cfce48375422",
      "email": "admin@bilcode.id",
      "full_name": "Super Admin",
      "role": "admin",
      "created_at": "2026-11-01T10:00:00Z"
    }
  }
  ```

---

## 2. Machine Learning Inference Endpoint

### `POST /predict`
Melakukan klasifikasi gambar sampah menggunakan model Transfer Learning (MobileNetV2).
* **Auth:** Public atau `Bearer <token>`
* **Content-Type:** `multipart/form-data`
* **Form Field:**
  * `file`: Binary image file (`image/jpeg`, `image/png`, `image/webp`)
* **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "data": {
      "category": "Plastic Waste",
      "confidence": 0.9421,
      "confidence_percentage": "94.21%",
      "category_id": 2,
      "probabilities": {
        "Organic Waste": 0.0312,
        "Plastic Waste": 0.9421,
        "Paper Waste": 0.0267
      }
    }
  }
  ```

---

## 3. Waste Reports Management

### `POST /reports`
Membuat laporan sampah baru (dari Mobile App / Web).
* **Auth:** `Bearer <token>`
* **Content-Type:** `multipart/form-data`
* **Form Fields:**
  * `file`: Foto bukti sampah (Binary)
  * `title`: "Tumpukan botol plastik di pinggir selokan"
  * `description`: "Botol plastik menumpuk menyumbat aliran air."
  * `category_id`: 2 (bisa didapat dari rekomendasi `/predict`)
  * `latitude`: -6.2088
  * `longitude`: 106.8456
  * `address_note`: "Jl. Ahmad Yani No. 12, depan ruko"
* **Response `201 Created`:**
  ```json
  {
    "status": "success",
    "message": "Report submitted successfully",
    "data": {
      "id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
      "title": "Tumpukan botol plastik di pinggir selokan",
      "image_url": "https://api.yourdomain.com/uploads/reports/e0b57e7a.jpg",
      "detected_category": "Plastic Waste",
      "ai_confidence": 0.9421,
      "status": "Pending",
      "created_at": "2026-11-01T12:30:00Z"
    }
  }
  ```

---

### `GET /reports`
Mengambil daftar laporan sampah (Mendukung filter, search, & pagination).
* **Auth:** `Bearer <token>`
* **Query Parameters:**
  * `status`: `Pending | In Progress | Completed | Rejected` (Opsional)
  * `category_id`: `1 | 2 | 3` (Opsional)
  * `search`: string keyword pencarian (judul / deskripsi / alamat)
  * `page`: integer (default: 1)
  * `limit`: integer (default: 10)
* **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "meta": {
      "total_items": 45,
      "current_page": 1,
      "total_pages": 5,
      "limit": 10
    },
    "data": [
      {
        "id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
        "title": "Tumpukan botol plastik",
        "category": {
          "id": 2,
          "name": "Plastic Waste",
          "badge_color": "#0284c7"
        },
        "reporter": {
          "id": "7c8e9b81-64d4-482a-bc91-2489e24f4692",
          "full_name": "Darell Rangga"
        },
        "image_url": "https://api.yourdomain.com/uploads/reports/e0b57e7a.jpg",
        "latitude": -6.2088,
        "longitude": 106.8456,
        "status": "Pending",
        "created_at": "2026-11-01T12:30:00Z"
      }
    ]
  }
  ```

---

### `PATCH /reports/{id}/status`
Mengubah status laporan (Khusus Role: `admin`).
* **Auth:** `Bearer <token>` (Admin Only)
* **Request Body (`application/json`):**
  ```json
  {
    "status": "In Progress",
    "admin_notes": "Tim truk kebersihan armada #3 sedang dikerahkan ke lokasi."
  }
  ```
* **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "message": "Report status updated to In Progress",
    "data": {
      "id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
      "status": "In Progress",
      "admin_notes": "Tim truk kebersihan armada #3 sedang dikerahkan ke lokasi.",
      "updated_at": "2026-11-01T13:00:00Z"
    }
  }
  ```

---

## 4. Admin Dashboard Metrics

### `GET /dashboard/stats`
Mengambil statistik agregasi untuk visualisasi widget dashboard web.
* **Auth:** `Bearer <token>` (Admin)
* **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "data": {
      "summary": {
        "total_reports": 142,
        "pending_count": 18,
        "in_progress_count": 12,
        "completed_count": 105,
        "rejected_count": 7,
        "completion_rate_percent": 73.94
      },
      "category_distribution": [
        { "category": "Organic Waste", "count": 64, "percentage": 45.07 },
        { "category": "Plastic Waste", "count": 52, "percentage": 36.62 },
        { "category": "Paper Waste", "count": 26, "percentage": 18.31 }
      ],
      "recent_activities": [
        {
          "report_id": "e0b57e7a-cbb1-4df2-b88d-0f9c2d155829",
          "action": "Status changed to In Progress",
          "timestamp": "2026-11-01T13:00:00Z"
        }
      ]
    }
  }
  ```
