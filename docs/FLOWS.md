# System Workflows & Sequence Diagrams (FLOWS)
## Smart Waste Management System (SWMS)

> 🎨 **Diagram Design Hub:** Versi visual editorial beresolusi tinggi (self-contained SVG/HTML) tersedia di:
> - 🔄 **State Machine Standalone:** [`docs/diagrams/report-lifecycle-state.html`](diagrams/report-lifecycle-state.html)
> - ⚡ **Citizen Reporting Sequence Standalone:** [`docs/diagrams/citizen-reporting-sequence.html`](diagrams/citizen-reporting-sequence.html)
> - 🌐 **Interactive Diagram Hub:** [`docs/diagrams/index.html`](diagrams/index.html)

> Dokumen ini memetakan seluruh alur kerja operasional, transisi *state machine*, diagram sekuens (*sequence diagram*), dan penanganan kondisi kritis (*edge cases*) untuk memastikan sistem bekerja presisi dari hulu ke hilir.

---

## 1. Waste Report Lifecycle (State Machine)

Setiap laporan sampah melewati siklus hidup dengan aturan transisi ketat untuk menjamin integritas data audit (*audit trail*).

```mermaid
stateDiagram-v2
    [*] --> Pending: Warga submit laporan via Mobile
    
    Pending --> In_Progress: Admin memverifikasi & menugaskan petugas
    Pending --> Rejected: Admin menolak (Foto buram/duplikat/iseng)
    
    In_Progress --> Completed: Petugas membersihkan sampah & unggah bukti
    In_Progress --> Rejected: Dibatalkan (Akses jalan tertutup/bukan sampah)
    
    Completed --> [*]
    Rejected --> [*]

    note right of Pending
      - Tercatat di database
      - Kategori dianalisis model AI
      - Lokasi GPS terkunci
    end note

    note right of In_Progress
      - Armada dinas dikerahkan
      - Log audit tercatat di report_logs
    end note

    note right of Completed
      - resolved_at terisi timestamp
      - Statistik penyelesaian naik
    end note
```

### Aturan Transisi Status
| Dari Status | Ke Status | Aktor yang Berhak | Syarat & Efek Samping |
| :--- | :--- | :--- | :--- |
| `[Draft]` | **`Pending`** | Citizen (Mobile/Web) | Foto valid, GPS latitude/longitude tidak null. Notifikasi status masuk. |
| `Pending` | **`In Progress`** | Admin / Operator | Wajib mengisi catatan disposisi (`admin_notes`). Buat entri di `report_logs`. |
| `Pending` | **`Rejected`** | Admin | Wajib mengisi alasan penolakan (misal: "Foto bukan sampah", "Duplikat"). |
| `In Progress` | **`Completed`**| Admin | `resolved_at` otomatis terisi waktu saat ini. Laporan ditutup. |
| `In Progress` | **`Rejected`** | Admin | Jika armada tiba di lokasi namun titik sampah tidak ditemukan. |

---

## 2. Alur Utama 1: Pembuatan Laporan Sampah dengan AI & GPS (Mobile User)

```mermaid
sequenceDiagram
    autonumber
    actor User as Warga (Mobile App)
    participant Flutter as Flutter Client
    participant GPS as Device GPS (Geolocator)
    participant API as FastAPI Backend
    participant ML as PyTorch Model (MobileNetV2)
    participant DB as PostgreSQL Database
    participant Storage as File Storage

    User->>Flutter: Buka Form "Laporkan Sampah"
    Flutter->>GPS: Request getCurrentPosition()
    GPS-->>Flutter: Return Coordinates (Lat, Long, Accuracy)
    
    User->>Flutter: Ambil foto sampah (Kamera / Galeri)
    Flutter->>API: POST /api/v1/predict (Multipart image)
    API->>ML: Preprocess (224x224) & Inference
    ML-->>API: Result { predicted_class: "Plastic Waste", confidence: 0.94 }
    API-->>Flutter: 200 OK with AI Prediction Result
    
    Flutter-->>User: Tampilkan Foto + Label AI ("Sampah Plastik, 94%")
    User->>Flutter: Konfirmasi / Koreksi Kategori + Input Catatan Alamat
    User->>Flutter: Tekan tombol "Kirim Laporan"
    
    Flutter->>API: POST /api/v1/reports (Multipart: photo, metadata, GPS)
    API->>Storage: Simpan file foto (Generate safe filename UUID)
    Storage-->>API: Return Image URL
    API->>DB: INSERT INTO waste_reports & INSERT INTO report_logs
    DB-->>API: Return created report record
    API-->>Flutter: 201 Created { report_id, status: "Pending" }
    Flutter-->>User: Tampilkan SnackBar Sukses & Navigasi ke Riwayat Laporan
```

---

## 3. Alur Utama 2: Tinjau & Update Status Laporan (Web Admin)

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Petugas Kebersihan (Web Admin)
    participant Next as Next.js Dashboard
    participant API as FastAPI Backend
    participant DB as PostgreSQL Database

    Admin->>Next: Buka Menu "Laporan Sampah"
    Next->>API: GET /api/v1/reports?status=Pending&page=1
    API->>DB: SELECT reports WHERE status = 'Pending' ORDER BY created_at DESC
    DB-->>API: Return Result Set + Pagination Meta
    API-->>Next: 200 OK with Report Data
    Next-->>Admin: Render Tabel Laporan dengan Badge Kuning (Pending)

    Admin->>Next: Klik "Tinjau Laporan" pada baris #RPT-001
    Next-->>Admin: Buka Modal Detail (Foto bukti, Pin Peta GPS, AI Confidence)
    
    Admin->>Next: Pilih Status "In Progress" & Ketik "Armada Truk #3 Meluncur"
    Next->>API: PATCH /api/v1/reports/{id}/status (Payload: { status, admin_notes })
    API->>DB: UPDATE waste_reports SET status = 'In Progress', admin_notes = ...
    API->>DB: INSERT INTO report_logs (report_id, actor_id, previous_status, new_status, remarks)
    DB-->>API: Commit Transaction
    API-->>Next: 200 OK { status: "success" }
    Next-->>Admin: Update status badge di tabel menjadi Biru (In Progress) & Toast Success
```

---

## 4. Alur Autentikasi & Otorisasi Berbasis Peran (RBAC)

```mermaid
sequenceDiagram
    autonumber
    actor Client as User / Admin
    participant App as Web / Mobile
    participant API as FastAPI Backend
    participant DB as PostgreSQL Database

    Client->>App: Input Email & Password
    App->>API: POST /api/v1/auth/login
    API->>DB: SELECT * FROM users WHERE email = ?
    DB-->>API: User record (with password_hash & role)
    API->>API: Verify Password (Bcrypt)
    alt Password Salah
        API-->>App: 401 Unauthorized ("Email atau password salah")
    else Password Benar
        API->>API: Generate JWT Access Token (Claims: sub=user_id, role=admin/user, exp)
        API-->>App: 200 OK { access_token, token_type: "bearer", user: { role, ... } }
        App->>App: Simpan Token di Secure Storage / Cookies
    end

    Note over App,API: Request ke Rute Khusus Admin (/api/v1/dashboard/stats)
    App->>API: GET /api/v1/dashboard/stats (Header: Authorization: Bearer <token>)
    API->>API: Decode JWT & Cek Role
    alt Role != 'admin'
        API-->>App: 403 Forbidden ("Hanya admin yang berhak mengakses resource ini")
    else Role == 'admin'
        API->>DB: Query Metrik Statistik
        DB-->>API: Aggregated Data
        API-->>App: 200 OK with Statistics
    end
```

---

## 5. Penanganan Kondisi Khusus & Kegagalan (Edge Cases)

### A. Kondisi: GPS Perangkat Tidak Aktif / Izin Ditolak
* **Gejala:** User mematikan lokasi di HP atau menolak izin GPS saat install.
* **Solusi Penanganan:**
  1. Aplikasi Flutter menampilkan dialog edukasi ramah: *"Izin lokasi dibutuhkan agar petugas tahu letak tumpukan sampah."*
  2. Jika user tetap menolak, aplikasi menyediakan input manual: **"Tulis Patokan Alamat Lengkap"** dan mengisi koordinat default pusat kota (misal: Balai Kota Jakarta) dengan flag `is_approximate_gps = true`.

### B. Kondisi: Tingkat Keyakinan AI Rendah (*Low Confidence* $< 50\%$)
* **Gejala:** Foto sampah diambil malam hari, gelap, buram, atau terlalu jauh.
* **Solusi Penanganan:**
  1. Endpoint `/predict` mengembalikan `confidence < 0.50`.
  2. Aplikasi Mobile tidak memaksakan auto-select, melainkan menampilkan peringatan halus: *"Foto agak buram. Mohon bantu pilih kategori sampah secara manual di bawah ini."*
  3. User tetap bisa memilih kategori secara manual (Organik, Plastik, atau Kertas).

### C. Kondisi: Koneksi Internet Terputus Saat Upload Foto
* **Gejala:** Pengguna berada di area sinyal lemah saat mengunggah foto berukuran beberapa MB.
* **Solusi Penanganan:**
  1. Aplikasi Flutter melakukan kompresi gambar lokal terlebih dahulu (maksimal resolusi $1080\text{p}$, kualitas $80\%$, ukuran $\le 800\text{ KB}$) sebelum dikirim via HTTP.
  2. Implementasi timeout 15 detik dengan tombol *Retry* otomatis tanpa menghapus data formulir yang sudah diisi.
