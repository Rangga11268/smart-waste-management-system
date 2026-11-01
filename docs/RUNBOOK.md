# Developer Runbook & Evaluator Walkthrough Guide
## Smart Waste Management System (SWMS)

> Dokumen operasional untuk menjalankan aplikasi secara lokal, kredensial akun uji coba (*seed data*), dan skenario demo untuk penguji / rekaman video presentasi ($\le 10$ menit).

---

## 1. Kredensial Uji Coba Default (Seed Data)

Untuk mempermudah penguji (reviewer Bilcode) langsung mencoba tanpa harus mendaftar dari nol:

| Role | Email | Password | Hak Akses |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@bilcode.id` | `Admin123!` | Akses Web Dashboard, filter laporan, update status, lihat audit log |
| **Warga Pelapor**| `user@bilcode.id` | `User123!` | Akses Mobile Flutter & Web, buat laporan sampah, lihat riwayat |

---

## 2. Quickstart Langkah Menjalankan Proyek Lokal

### A. Backend & AI Inference (Port 8000)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Menjalankan server lokal
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Buka browser: `http://localhost:8000/docs` (Swagger UI siap diuji).

### B. Web Dashboard Admin (Port 3000)
```bash
cd web
npm install
npm run dev
```
* Buka browser: `http://localhost:3000` (Login dengan `admin@bilcode.id`).

### C. Mobile Application (Flutter)
```bash
cd mobile
flutter pub get
flutter run
```

---

## 3. Skenario Demo Penguji (Script Video Presentasi $\le 10$ Menit)

Gunakan alur cerita terstruktur ini saat merekam video demo:

| Menit | Segmen Presentasi | Aksi yang Ditampilkan di Layar |
| :---: | :--- | :--- |
| **00:00 - 01:30** | **Pembukaan & Arsitektur** | Tunjukkan slide ringkas / dokumen `docs/ARCHITECTURE.md`. Jelaskan mengapa memilih FastAPI unified + Next.js + Flutter + PostgreSQL. |
| **01:30 - 03:30** | **Model ML & Evaluasi** | Tunjukkan script `train.py` & `evaluate.py`. Perlihatkan grafik **Confusion Matrix** dan **Classification Report** (Akurasi $\ge 85\%$). Uji inferensi cepat di terminal. |
| **03:30 - 06:00** | **Mobile App (Warga)** | Buka aplikasi Flutter di HP/Emulator: Login warga $\rightarrow$ Form Laporan $\rightarrow$ Ambil foto botol plastik $\rightarrow$ AI mendeteksi *"Plastic Waste 94%"* $\rightarrow$ GPS terkunci $\rightarrow$ Kirim Laporan $\rightarrow$ Masuk ke Riwayat (Status: `Pending`). |
| **06:00 - 08:30** | **Web Admin Dashboard** | Buka Web Next.js: Login admin $\rightarrow$ Lihat metrik statistik $\rightarrow$ Buka tabel laporan $\rightarrow$ Buka modal detail laporan yang baru dibuat dari mobile $\rightarrow$ Ubah status jadi `In Progress` $\rightarrow$ Ubah ke `Completed`. |
| **08:30 - 09:30** | **Verifikasi Database & API** | Buka `http://localhost:8000/docs` (Swagger UI) dan tabel database (tunjukkan entri di `waste_reports` dan `report_logs`). |
| **09:30 - 10:00** | **Penutup** | Ringkasan pencapaian 10 deliverables brief Bilcode. |
