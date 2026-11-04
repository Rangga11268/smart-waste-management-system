# Panduan Persiapan & Naskah Video Demo
## Smart Waste Management System (SWMS)
**Take-Home Technical Assessment — PT Bilcode Teknologi Indonesia**

---

## 📋 1. Checklist Persiapan Teknis (Sebelum Record)

| Item | Status & Keterangan | URL / Kredensial |
| :--- | :--- | :--- |
| **Web Production (Vercel)** | ✅ Live 24/7 | `https://web-ruby-omega-37.vercel.app` |
| **Backend API (Railway)** | ✅ Live 24/7 (Port 8080) | `https://smart-waste-management-system-production.up.railway.app/docs` |
| **GitHub Release APK** | ✅ v1.0.0 Release (49.6 MB) | `https://github.com/Rangga11268/smart-waste-management-system/releases/tag/v1.0.0` |
| **Akun Super Admin** | Akses penuh triage & status | Email: `admin@bilcode.id`<br>Password: `Admin123!` |
| **Akun Warga Pelapor** | Akses telemetri kota & lapor | Email: `user@bilcode.id`<br>Password: `User123!` |
| **Software Perekam** | Rekomendasi 1080p 60fps | OBS Studio atau Xbox Game Bar (`Win + G`) |
| **Audio** | Suara jernih tanpa noise | Gunakan mic headset / earphone |

### Layout Layar yang Direkomendasikan:
- **Jendela Kiri (40%)**: Tampilan Mobile Citizen App (bisa via Emulator Android Studio, atau cermin layar HP via *scrcpy*).
- **Jendela Kanan (60%)**: Browser Chrome dengan 3 tab siap buka:
  1. Tab 1: Web Portal (`https://web-ruby-omega-37.vercel.app/login`)
  2. Tab 2: Swagger REST API (`https://smart-waste-management-system-production.up.railway.app/docs`)
  3. Tab 3: GitHub Releases (`https://github.com/Rangga11268/smart-waste-management-system/releases/tag/v1.0.0`)

---

## ⏱️ 2. Timeline Breakdown (Total: ~5 Menit 45 Detik)

```
0:00 ─── 0:45  [Scene 1] Pembuka & Arsitektur End-to-End
0:45 ─── 2:20  [Scene 2] Demo Mobile App: Pelaporan, AI Inference & Offline-First
2:20 ─── 4:10  [Scene 3] Demo Web Admin: Nordic Minimalist, GIS Map & Triage Action Cards
4:10 ─── 5:15  [Scene 4] Backend FastAPI, Skalabilitas Cloud & Artefak Release
5:15 ─── 5:45  [Scene 5] Penutup & Kesiapan Evaluasi Teknis
```

---

## 🎙️ 3. Naskah Presentasi Lengkap (Kata-per-Kata)

### Scene 1: Pembuka & Gambaran Solusi (0:00 – 0:45)
*Layar: Menampilkan landing page atau dashboard web SWMS dengan arsitektur bersih.*

> "Halo tim penilai Bilcode Technology. Perkenalkan, saya **[Nama Anda]**. 
> 
> Hari ini saya mendemonstrasikan **Smart Waste Management System (SWMS)** — sebuah platform terintegrasi cerdas berbasis AI untuk akselerasi pelaporan sampah liar, klasifikasi otomatis, dan orkestrasi penanganan kebersihan perkotaan.
> 
> Sistem ini dibangun dengan arsitektur modern full-stack yang sudah **live production 24/7 di cloud**:
> 1. **Mobile Application** berbasis Flutter untuk kemudahan warga melapor, didukung kapabilitas *Offline-First*.
> 2. **AI Vision Classifier** berbasis MobileNetV2 Transfer Learning untuk klasifikasi citra sampah instan.
> 3. **Backend Service** berbasis FastAPI yang telah dideploy di Railway cloud.
> 4. **Web Management Console** berbasis Next.js 14 dengan pendekatan desain *Nordic Minimalism* yang dideploy di Vercel.
> 
> Mari kita mulai langsung dari pengalaman warga saat menemukan tumpukan sampah."

---

### Scene 2: Mobile Citizen App, AI Vision & Offline-First (0:45 – 2:20)
*Layar: Arahkan fokus ke Aplikasi Mobile Flutter di HP/Emulator.*

> "Sekarang kita beralih ke aplikasi mobile SWMS Citizen. Antarmukanya dirancang sangat intuitif agar warga dapat melapor dalam hitungan detik.
> 
> *(Aksi: Tekan tombol 'Buat Laporan / Lapor Sampah')*
> 
> Langkah pertama, warga mengambil foto atau mengunggah gambar sampah dari galeri. Di sini saya memilih foto botol plastik bekas.
> 
> *(Aksi: Pilih foto botol plastik, biarkan inferensi AI berjalan)*
> 
> Secara otomatis, pipeline Machine Learning **MobileNetV2** langsung menganalisis gambar dan mendeteksi kategori **Plastic Waste** dengan confidence score di atas 90%. Kategori dan estimasi akurasi ini terisi otomatis tanpa mengharuskan warga menebak jenis sampah.
> 
> *(Aksi: Tunjukkan kolom koordinat dan alamat GPS)*
> 
> Lokasi koordinat satelit GPS juga terkunci secara presisi, dilengkapi reverse-geocoding alamat jalan otomatis.
> 
> Selain itu, aplikasi ini memiliki keunggulan **Offline-First**. Apabila warga berada di titik *blank spot* tanpa koneksi internet, laporan tidak akan hilang melainkan tersimpan sebagai draft terenkripsi lokal dan otomatis tersinkronisasi begitu sinyal kembali tersedia.
> 
> *(Aksi: Klik tombol 'Kirim Laporan')*
> 
> Laporan berhasil terkirim ke cloud server, dan warga langsung menerima kode tracking laporan. Sekarang mari kita lihat bagaimana dinas kebersihan merespons laporan ini di Web Console."

---

### Scene 3: Web Admin Dashboard, GIS Mapping & Triage (2:20 – 4:10)
*Layar: Pindah ke browser, buka Web Admin Vercel.*

> "Sekarang kita berada di Web Portal SWMS yang sudah live di Vercel.
> 
> *(Aksi: Login menggunakan admin@bilcode.id / Admin123!)*
> 
> Desain antarmuka dashboard ini mengadopsi filosofi **Nordic Minimalism** — bersih, berfokus pada informasi penting (*high contrast*), tipografi presisi, dan bebas dari elemen dekoratif yang tidak perlu.
> 
> *(Aksi: Tunjukkan ringkasan metrik dan Peta GIS)*
> 
> Di halaman utama, admin disajikan telemetri operasional real-time: total laporan, rasio tuntas, distribusi kategori sampah, serta **peta interaktif GIS Leaflet** yang memetakan sebaran titik sampah di seluruh kota.
> 
> *(Aksi: Klik menu 'Laporan Sampah' di navigasi)*
> 
> Sekarang kita masuk ke konsol manajemen laporan. Terlihat laporan botol plastik yang baru saja kita submit dari mobile sudah masuk di baris teratas dengan status 'Menunggu Validasi'.
> 
> *(Aksi: Klik laporan tersebut hingga Modal Detail terbuka)*
> 
> Untuk alur triase operasional, admin tidak dihadapkan pada dropdown yang membingungkan. Kami merancang **Action Cards ber-kontras tinggi** dengan bahasa operasional yang tegas:
> - **Tugaskan Armada Lapangan** (In Progress)
> - **Tandai Selesai Ditangani** (Completed)
> - **Tolak Laporan** (Rejected)
> 
> Admin juga dapat memanfaatkan **Quick Disposition Notes** untuk memilih catatan penugasan hanya dalam 1 klik.
> 
> *(Aksi: Klik 'Tugaskan Armada Lapangan', pilih catatan cepat armada, klik 'Perbarui Status')*
> 
> Status langsung terbarui secara instan. Pada panel riwayat di bawah, sistem mencatat **Audit Trail** lengkap: siapa yang mengubah status, catatan instruksi armada, dan stempel waktu presisi tanpa kehilangan data."

---

### Scene 4: Backend API, Skalabilitas Cloud & GitHub Release (4:10 – 5:15)
*Layar: Buka tab Swagger Docs Railway, lalu tab GitHub Release.*

> "Dari sisi keandalan infrastruktur backend dan standar rekayasa perangkat lunak:
> 
> *(Aksi: Buka tab Swagger `/docs` di Railway)*
> 
> Backend dibangun menggunakan **FastAPI** dengan arsitektur modular:
> - Menggunakan autentikasi berbasis JWT dengan Role-Based Access Control (RBAC) yang membedakan hak akses Admin dan Warga.
> - Mendukung dual-database engine (PostgreSQL untuk skala enterprise dan fallback otomatis ke SQLite lokal untuk ketahanan layanan).
> - Endpoint inferensi ML `/api/v1/predict` melayani klasifikasi berkecepatan tinggi dengan konsumsi memori yang sangat efisien.
> 
> *(Aksi: Buka tab GitHub Release v1.0.0)*
> 
> Seluruh artefak proyek — mulai dari diagram arsitektur C4, diagram ERD database, dokumentasi API, hingga **file instalasi APK release (`swms_citizen_release.apk`)** — telah dirilis secara resmi di GitHub Release v1.0.0. Tim penilai dapat langsung mengunduh dan menguji APK ini di perangkat Android fisik."

---

### Scene 5: Penutup (5:15 – 5:45)
*Layar: Kembali ke landing page atau dashboard SWMS.*

> "Sebagai kesimpulan, Smart Waste Management System ini dirancang tidak hanya untuk memenuhi seluruh kriteria penilaian teknis Bilcode Technology, tetapi juga siap diimplementasikan sebagai solusi nyata untuk kota cerdas masa kini.
> 
> Mulai dari pengalaman warga di mobile, keandalan model ML, hingga kemudahan operasional dinas di web, seluruh alur telah teruji dan berjalan sempurna di cloud 24/7.
> 
> Terima kasih banyak atas waktu dan perhatian tim penilai Bilcode Technology. Saya siap mendiskusikan implementasi teknis lebih dalam pada sesi berikutnya. Salam hangat!"

---

## 🎯 4. Cheat-Sheet Tanya Jawab (Antisipasi Pertanyaan Penilai)

| Pertanyaan Penguji | Poin Jawaban Kunci |
| :--- | :--- |
| **Kenapa memilih MobileNetV2?** | *"MobileNetV2 menggunakan depthwise separable convolutions yang sangat ringan (ukuran model <15MB), menjadikannya ideal untuk inferensi CPU berkecepatan tinggi di backend maupun on-device edge tanpa memerlukan GPU mahal."* |
| **Bagaimana fitur Offline-First di mobile bekerja?** | *"Aplikasi mobile menggunakan Hive/local storage. Saat device offline, laporan disimpan sebagai draft lokal lengkap dengan metadata foto dan koordinat terakhir. Saat konektivitas pulih, background sync otomatis mengirimkan antrean ke REST API."* |
| **Bagaimana menangani keamanan data & autentikasi?** | *"Menggunakan JWT standar dengan algoritma HS256, enkripsi password Bcrypt asli, validasi skema Pydantic v2 di pintu masuk request, dan pembagian hak akses ketat (RBAC) antara Super Admin dan Warga Pelapor."* |
| **Mengapa desain web bernuansa minimalis?** | *"Mengikuti prinsip Nordic Minimalism: kontras tinggi untuk keterbacaan petugas lapangan, tipografi terstruktur, tata letak responsif tanpa elemen dekoratif berlebih yang memperlambat render, memenuhi standar aksesibilitas WCAG."* |
