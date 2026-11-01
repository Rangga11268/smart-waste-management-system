# Product Requirements Document (PRD)
## Smart Waste Management System (SWMS)
**Candidate:** Darell Rangga Putra Rachman  
**Assessment:** Take-Home Technical Coding Test — Fullstack Developer | Bilcode Technology  
**Deadline:** 6 November 2026 (5 Hari Kalender)  
**Passing Grade:** Minimum 75/100  

---

### 1. Product Overview & Problem Statement
Pertumbuhan volume sampah perkotaan sering kali tidak terkelola dengan efisien akibat keterlambatan pelaporan, minimnya kategorisasi sampah dari sumbernya, dan ketiadaan tracking penanganan sampah secara real-time.

**Smart Waste Management System (SWMS)** adalah ekosistem multi-platform yang menghubungkan:
1. **Masyarakat / User (Mobile App Flutter):** Melaporkan tumpukan sampah secara cepat dengan bantuan **AI Camera Recognition** (auto-detect jenis sampah: Organik, Plastik, Kertas) + Geotagging GPS otomatis.
2. **Pemerintah / Operator Kebersihan (Web Admin Dashboard):** Memonitor sebaran titik sampah, metrik statistik harian, alur validasi laporan, dan perubahan status penanganan hingga tuntas.
3. **Core Engine (FastAPI & PyTorch ML):** Menyediakan REST API terpusat, otentikasi JWT berbasis peran, serta inferensi AI klasifikasi sampah.

---

### 2. User Personas & Roles

| Role | Deskripsi | Hak Akses Utama |
| :--- | :--- | :--- |
| **Citizen / User** | Masyarakat umum pelapor sampah liar/penuh. | - Registrasi & Login (Mobile/Web)<br>- Buat laporan sampah (Foto + AI Scan + GPS + Deskripsi)<br>- Pantau riwayat & timeline status laporannya. |
| **Admin / Operator** | Petugas dinas kebersihan / supervisor lapangan. | - Dashboard metrik & analitik ringkasan sampah<br>- Tinjau detail laporan, verifikasi foto & lokasi peta<br>- Update status: `Pending` ➔ `In Progress` ➔ `Completed` / `Rejected`<br>- Manajemen master data & akun user. |

---

### 3. Functional Requirements (FR)

#### A. Machine Learning Service (Bobot 20% + 15%)
* **FR-ML-01:** Model mengklasifikasikan 3 kategori sampah: `Organic Waste`, `Plastic Waste`, dan `Paper Waste`.
* **FR-ML-02:** Dataset minimal 150 gambar (50 gambar/kategori) dengan data augmentation.
* **FR-ML-03:** Arsitektur transfer learning (MobileNetV2) dengan akurasi pengujian minimal **$\ge 80\%$** (target $\ge 85\%$).
* **FR-ML-04:** Evaluasi model menghasilkan visualisasi *Confusion Matrix*, grafik *Loss/Accuracy*, dan metrik *Precision/Recall/F1-Score*.
* **FR-ML-05:** Endpoint inferensi `POST /api/v1/predict` menerima multipart image dan mengembalikan `{ predicted_class: string, confidence: float }`.

#### B. Backend & REST API (FastAPI)
* **FR-BE-01:** Autentikasi menggunakan JWT Token dengan enkripsi password (Bcrypt/Argon2).
* **FR-BE-02:** Role-based Access Control (`admin` & `user`).
* **FR-BE-03:** CRUD Laporan Sampah: Create, Read (filter, sort, search, pagination), Update Status, Delete.
* **FR-BE-04:** Penyimpanan bukti foto sampah (Cloud storage/Local static serve) dan tagging koordinat latitude/longitude.
* **FR-BE-05:** OpenAPI / Swagger UI interaktif di `/docs`.

#### C. Web Admin Dashboard (Next.js / Tailwind) (Bobot 25%)
* **FR-WB-01:** Login form khusus Admin & User.
* **FR-WB-02:** Widget statistik: Total Laporan, Laporan Selesai, Rasio Kategori Sampah, dan Laporan Tertunda.
* **FR-WB-03:** Tabel data laporan interaktif dengan pencarian teks dan filter status (`Pending`, `In Progress`, `Completed`, `Rejected`).
* **FR-WB-04:** Modal tinjau laporan: Foto bukti, lokasi GPS (link Google Maps), kategori terdeteksi AI, dan tombol aksi update status.
* **FR-WB-05:** Manajemen Pengguna (list user & status aktivasi).
* **FR-WB-06:** Tampilan responsif (Mobile, Tablet, Desktop).

#### D. Mobile Application (Flutter) (Bobot 20%)
* **FR-MB-01:** Layar Registrasi & Login.
* **FR-MB-02:** Home Dashboard menampilkan ringkasan laporan aktif pengguna.
* **FR-MB-03:** Form Laporan Baru:
  - Tombol Kamera / Galeri untuk mengambil foto sampah.
  - Integrasi AI: Otomatis mendeteksi kategori sampah via API `/predict`.
  - Geotagging: Mengambil koordinat GPS perangkat secara otomatis (`geolocator`).
  - Input catatan/deskripsi tambahan.
* **FR-MB-04:** Layar Riwayat Laporan (History) dengan indikator warna status (`Pending` kuning, `In Progress` biru, `Completed` hijau, `Rejected` merah).

---

### 4. Non-Functional Requirements (NFR)
* **NFR-01 (Performance):** Respon inferensi AI di bawah 800ms pada CPU.
* **NFR-02 (Security):** Semua rute privat wajib menyertakan Bearer Token JWT; CORS terkonfigurasi aman.
* **NFR-03 (Reliability):** Database menggunakan skema relasional dengan foreign key integrity.
* **NFR-04 (Usability):** UI bersih (*anti-slop*), kontras warna tinggi, navigasi intuitif.

---

### 5. Delivery Matrix (10 Checklist Penilaian Bilcode)
- [ ] 1. GitHub Repository Publik (Monorepo terstruktur).
- [ ] 2. Link Live Demo Website.
- [ ] 3. File APK Android (Release build).
- [ ] 4. Dokumentasi API (Swagger UI / Postman).
- [ ] 5. Database Schema & ERD (Format Gambar & Markdown).
- [ ] 6. Source code dan file model ML (`waste_model.pth` / `.onnx`).
- [ ] 7. Dataset 150+ gambar beserta sitasi sumbernya.
- [ ] 8. Hasil evaluasi model (Grafik & Laporan Klasifikasi).
- [ ] 9. README komprehensif (Setup, Arsitektur, Environment).
- [ ] 10. Video demo presentasi ($\le$ 10 menit).
