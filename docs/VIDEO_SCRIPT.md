# Panduan & Script Rekaman Video Demo SWMS ($\le$ 10 Menit)
## Bilcode Technology Fullstack Developer Technical Assessment

Dokumen ini adalah naskah presentasi terstruktur dan panduan rekaman video demo (*screencast*) berdurasi maksimal 10 menit untuk pengujian teknis **Smart Waste Management System (SWMS)**.

---

## ⏱️ Breakdown Alokasi Waktu (Total $\le$ 10 Menit)

| Bagian | Topik | Alokasi Waktu | Layar / Window |
|---|---|---|---|
| **Part 1** | Perkenalan Diri & Ringkasan Solusi SWMS | 00:00 - 01:30 (1.5 mnt) | Slide Judul / README & Arsitektur |
| **Part 2** | ML Pipeline: Dataset & PyTorch MobileNetV2 | 01:30 - 03:00 (1.5 mnt) | `confusion_matrix.png`, `accuracy_curve.png` |
| **Part 3** | Backend Core FastAPI & Interactive Swagger | 03:00 - 04:45 (1.75 mnt) | Browser: `http://localhost:8000/docs` |
| **Part 4** | Web Admin Dashboard (Next.js 14) | 04:45 - 07:15 (2.5 mnt) | Browser: `http://localhost:3000` |
| **Part 5** | Flutter Citizen Mobile App (Kamera, AI & GPS) | 07:15 - 09:15 (2.0 mnt) | Android Emulator / HP Fisik |
| **Part 6** | Kesimpulan & Q&A Readiness | 09:15 - 10:00 (0.75 mnt) | GitHub Repo & Penutupan |

---

## 🎙️ Naskah & Panduan Narasi Per Bagian

### Part 1: Perkenalan & Arsitektur Solusi (00:00 - 01:30)
- **Tampilan**: Buka browser pada halaman GitHub Monorepo `Rangga11268/smart-waste-management-system` atau `docs/ARCHITECTURE.md`.
- **Narasi yang Diucapkan**:
  > *"Halo tim penilai dan rekrutmen Bilcode Technology. Nama saya Rangga, dan ini adalah presentasi teknis serta demo sistem Smart Waste Management System (SWMS) yang saya kembangkan untuk Technical Assessment posisi Fullstack Developer.*
  >
  > *SWMS adalah solusi monorepo menyeluruh yang menghubungkan partisipasi warga (citizen reporting) dengan operasional kebersihan kota. Sistem ini dibangun dengan empat pilar utama:*
  > 1. *Machine Learning: PyTorch MobileNetV2 untuk klasifikasi sampah foto real-time.*
  > 2. *Backend: FastAPI bertenaga Python 3.12 dengan arsitektur dual database PostgreSQL & SQLite fallback, JWT RBAC, dan audit logging.*
  > 3. *Web Dashboard: Next.js 14 App Router dengan Tailwind CSS untuk admin memantau metrik dan meninjau laporan.*
  > 4. *Mobile App: Flutter Android untuk warga melapor dengan kamera, deteksi AI otomatis, dan geotagging GPS akurat.*
  >
  > *Mari kita masuk ke pilar pertama, yaitu Machine Learning Pipeline."*

---

### Part 2: Machine Learning Pipeline & Evaluasi (01:30 - 03:00)
- **Tampilan**: Buka gambar `accuracy_curve.png`, `confusion_matrix.png`, dan file `classification_report.txt`.
- **Narasi yang Diucapkan**:
  > *"Untuk model AI, saya menggunakan transfer learning berbasis arsitektur MobileNetV2 yang dioptimalkan untuk inferensi cepat di lingkungan komputasi CPU dan mobile.*
  >
  > *Dataset yang dikurasi terdiri dari 210 citra fotografi resolusi tinggi yang terbagi seimbang ke dalam 3 kelas utama: Organik, Plastik, dan Kertas (masing-masing 70 gambar), dengan rasio split 80% train dan 20% validation.*
  >
  > *Hasil pelatihan selama 15 epoch dengan Cosine Annealing learning rate schedule menghasilkan akurasi validasi akhir sebesar **92.86%** dengan Macro F1-score sebesar **0.9277**.*
  >
  > *Bisa kita lihat pada confusion matrix, kelas Organik dan Kertas mencapai precision 100%, dan model berhasil diekspor menjadi binary `waste_model.pth` berukuran 9.15 MB dengan latensi inferensi di bawah 80 milidetik."*

---

### Part 3: Backend API FastAPI & Swagger UI (03:00 - 04:45)
- **Tampilan**: Buka browser di `http://localhost:8000/docs` (Swagger UI).
- **Narasi yang Diucapkan**:
  > *"Sekarang kita beralih ke backend. Saya memilih FastAPI karena performanya yang asinkron, keamanan berbasis tipe Pydantic, dan auto-generated OpenAPI documentation.*
  >
  > *Di Swagger UI ini terdapat 5 modul endpoint utama:*
  > 1. *Auth Module: Registrasi dan login warga maupun admin yang menerbitkan JWT access token.*
  > 2. *ML Inference: `POST /api/v1/predict` yang menerima berkas foto dan langsung mengembalikan kategori, skor probabilitas, serta relasi category ID.*
  > 3. *Reports Module: `POST /api/v1/reports` multipart upload untuk bukti foto, metadata lokasi GPS, dan judul; serta listing laporan dengan paginasi dan filter.*
  > 4. *Dashboard & Categories: Menyediakan ringkasan KPI agregat dan master kategori.*
  > 5. *Users Module: Manajemen pengguna dengan proteksi role admin.*
  >
  > *Sistem database dirancang resilient: backend secara otomatis memprioritaskan koneksi PostgreSQL, namun bila server cloud sedang offline, sistem memiliki graceful fallback ke local SQLite database `swms_dev.db` tanpa crashing."*

---

### Part 4: Web Admin Dashboard — Next.js 14 (04:45 - 07:15)
- **Tampilan**: Buka `http://localhost:3000`. Login dengan `admin@bilcode.id` / `Admin123!`.
- **Narasi yang Diucapkan**:
  > *"Selanjutnya adalah Web Admin Dashboard yang dibangun menggunakan Next.js 14 App Router dan Tailwind CSS dengan desain bertema Eco-Tech Emerald.*
  >
  > *Pertama, halaman Analytics Dashboard menampilkan 4 KPI cards utama secara real-time: Total Laporan Masuk, Laporan Menunggu (Pending), Sedang Diproses (In Progress), dan Selesai (Completed), lengkap dengan distribusi kategori sampah.*
  >
  > *Kedua, halaman Manajemen Laporan Sampah. Di sini admin dapat menyaring laporan berdasarkan status, kategori, atau pencarian teks. Ketika kita klik salah satu laporan, terbuka Review Modal yang menampilkan foto bukti asli, lencana hasil prediksi AI MobileNetV2 dengan akurasi persentase, koordinat GPS dengan tautan langsung ke Google Maps, serta formulir status transit.*
  >
  > *Mari kita ubah status laporan dari 'Pending' menjadi 'In Progress' dengan catatan armada kebersihan. Sistem langsung mencatat perubahan ini ke dalam audit log `report_logs` yang tidak bisa dimanipulasi.*
  >
  > *Ketiga, halaman Manajemen Pengguna di mana admin dapat melihat seluruh akun terdaftar beserta total kontribusi laporannya."*

---

### Part 5: Flutter Citizen Mobile App (07:15 - 09:15)
- **Tampilan**: Buka Android Emulator atau scrcpy layar smartphone Android menjalankan `swms_mobile`.
- **Narasi yang Diucapkan**:
  > *"Sekarang mari kita uji Citizen Mobile App yang dibangun dengan Flutter.*
  >
  > *Aplikasi ini sudah berhasil dikompilasi menjadi standalone release APK berukuran 49.7 MB yang tersedia langsung di repositori.*
  >
  > *Saat aplikasi dibuka, warga disambut dengan dashboard ringkas dan tombol aksi 'Ambil Foto & Lapor Sekarang'.*
  >
  > *Ketika tombol kamera ditekan dan kita memilih foto sampah botol plastik:*
  > 1. *AI Smart Waste Scanner langsung melakukan inferensi ke endpoint `/predict` dan menampilkan banner hijau: 'Plastik - Akurasi 96%'.*
  > 2. *Secara simultan, plugin geolocator mengunci koordinat GPS perangkat secara otomatis.*
  > 3. *Warga cukup menambahkan catatan alamat atau patokan, lalu menekan tombol 'Kirim Laporan'.*
  >
  > *Laporan langsung terkirim dan muncul di tab 'Riwayat' dengan status badge warna amber (Pending). Ketika admin di web dashboard memperbarui status laporan tersebut, status di aplikasi mobile ini langsung ter-update secara sinkron."*

---

### Part 6: Penutup & Evaluasi Deliverables (09:15 - 10:00)
- **Tampilan**: Buka file `README.md` pada GitHub repo.
- **Narasi yang Diucapkan**:
  > *"Seluruh 10 deliverables wajib yang diminta oleh Bilcode Technology telah terpenuhi 100%: mulai dari monorepo GitHub, live preview, standalone Android release APK, dokumentasi OpenAPI & Swagger UI, database ERD schema, bobot model `waste_model.pth`, dataset 210 citra berlisensi, artefak evaluasi, hingga unit test suite backend dan frontend dengan pass rate 100%.*
  >
  > *Terima kasih banyak atas kesempatan pengujian teknis ini kepada tim Bilcode Technology. Saya siap untuk mendiskusikan implementasi ini lebih mendalam pada sesi wawancara teknis selanjutnya. Salam sehat dan terima kasih!"*
