# Panduan Persiapan & Naskah Video Demo (Natural & Relaxed)
## Smart Waste Management System (SWMS)
**Technical Assessment — PT Bilcode Teknologi Indonesia**

---

## 📋 1. Cheat Sheet Persiapan Sebelum Record

| Kebutuhan | Data / Akses |
| :--- | :--- |
| **Web Live (Vercel)** | `https://web-ruby-omega-37.vercel.app` |
| **Backend API Live (Railway)** | `https://smart-waste-management-system-production.up.railway.app/docs` |
| **Akun Admin (Full Akses)** | `admin@bilcode.id` / `Admin123!` |
| **Akun Warga (Pelapor)** | `user@bilcode.id` / `User123!` |
| **Aplikasi Mobile** | Jalankan via Emulator Android Studio atau Mirror HP fisik (scrcpy) |
| **Software Rekam** | OBS Studio / Xbox Game Bar (`Win + G`) — Mic aktif, resolusi 1080p |

---

## ⏱️ Alur & Estimasi Waktu (~5 Menit)

1. **00:00 - 00:45** | Intro santai & gambaran umum sistem.
2. **00:45 - 02:15** | Demo Mobile App: ambil foto, auto-deteksi AI, GPS, kirim laporan.
3. **02:15 - 03:45** | Demo Web Portal: tabel ringkas, masuk ke halaman detail laporan, triase admin, audit log.
4. **03:45 - 04:30** | Intip Backend & Cloud: FastAPI docs di Railway, Vercel deployment.
5. **04:30 - 05:00** | Closing singkat & to-the-point.

---

## 🎙️ Naskah Presentasi (Gaya Natural & Percaya Diri)

*(Tips: Bawakan dengan tempo santai, seperti lagi demo fitur ke sesama rekan engineer atau tech lead).*

---

### [00:00 - 00:45] Intro: Buka dengan Santai & Jelas

*(Aksi: Tampilkan layar desktop — buka halaman depan web SWMS)*

> "Halo tim penilai Bilcode Tech! Kenalin, saya **[Nama Kamu]**.
> 
> Hari ini saya mau mendemokan project yang udah saya bangun buat technical test ini, yaitu **Smart Waste Management System (SWMS)**.
> 
> Singkatnya, SWMS ini adalah platform end-to-end buat ngebantu warga ngelaporin tumpukan sampah liar, sekaligus ngebantu dinas kebersihan kota buat triage dan nanganin laporan itu secara real-time.
> 
> Project ini mencakup:
> - **Aplikasi Mobile** berbasis Flutter buat warga,
> - **AI Vision** berbasis PyTorch MobileNetV2 buat klasifikasi otomatis sampah,
> - **Backend REST API** pakai FastAPI yang udah dideploy di Railway,
> - dan **Web Portal** pakai Next.js 14 yang udah live di Vercel.
> 
> Supaya nggak kelamaan di slide atau teori, yuk kita langsung cobain alurnya dari kacamata warga dulu."

---

### [00:45 - 02:15] Demo Mobile: Alur Warga & AI Classifier

*(Aksi: Pindah fokus ke aplikasi mobile di emulator / HP)*

> "Nah, sekarang kita ada di aplikasi mobile SWMS.
> 
> Anggap saya seorang warga yang lagi jalan di sekitar lingkungan dan nemu tumpukan sampah plastik yang berserakan.
> 
> *(Aksi: Tap tombol 'Buat Laporan / Lapor Sampah')*
> 
> Di sini warga tinggal ambil foto atau pilih dari galeri. Saya coba ambil foto tumpukan botol plastik ini ya.
> 
> *(Aksi: Pilih foto botol plastik, biarkan loading AI sebentar)*
> 
> Nah, bisa kita lihat di sini — begitu foto di-upload, model AI MobileNetV2 langsung jalan dan mendeteksi kalau ini adalah **Plastic Waste**, lengkap dengan tingkat keyakinan atau confidence score-nya di atas 90%. Jadi warga nggak perlu bingung nebak-nebak jenis sampahnya. Tapi kalau warga ngerasa kategorinya beda, mereka tetap bisa ganti secara manual.
> 
> *(Aksi: Tunjukin field koordinat & alamat)*
> 
> Lokasi koordinat GPS juga langsung ke-lock otomatis, plus sistem melakukan reverse-geocoding buat nampilin nama jalan atau patokan lokasi.
> 
> Selain itu, aplikasi mobile ini juga udah *offline-friendly*. Jadi kalau pas warga moto sinyal lagi drop, laporan bakal aman tersimpan di storage lokal dan otomatis ke-sync waktu sinyal balik lagi.
> 
> Sekarang kita isi deskripsi singkat, misalnya: *'Tumpukan botol plastik di pinggir jalan depan ruko'*, lalu kita tap **Kirim Laporan**.
> 
> *(Aksi: Tap 'Kirim Laporan', tunggu sampai ada alert sukses)*
> 
> Oke, laporan berhasil masuk ke sistem! Sekarang kita lihat gimana laporan ini diterima dan ditindaklanjuti sama petugas di Web Portal."

---

### [02:15 - 03:45] Demo Web Portal: Triase Operasional & Detail Page

*(Aksi: Pindah ke browser, buka web `https://web-ruby-omega-37.vercel.app`)*

> "Sekarang kita beralih ke Web Portal SWMS.
> 
> *(Aksi: Login pakai admin@bilcode.id / Admin123!)*
> 
> Begitu admin login, kita langsung disambut sama **Pusat Kendali Operasional**.
> Di sini tampil ringkasan metrik kota: total laporan masuk, berapa yang lagi diproses, tingkat penyelesaian, dan distribusi jenis sampah. Desainnya sengaja dibuat bersih dan fungsional dengan palet warna terstandarisasi, biar petugas lapangan nyaman mantau data dalam waktu lama.
> 
> Sekarang kita klik menu **Laporan Sampah**.
> 
> *(Aksi: Klik menu 'Laporan Sampah' di navigasi)*
> 
> Nah, di tabel ini kita bisa lihat laporan botol plastik yang barusan kita buat dari HP udah langsung muncul di baris teratas dengan status *'Menunggu Validasi'*.
> 
> Tabel ini sengaja kita bikin ringkas — cuma nampilin informasi esensial triase: judul, kategori, lokasi, waktu, dan status. Buat info lengkapnya, kita tinggal klik barisnya.
> 
> *(Aksi: Klik baris laporan tersebut untuk masuk ke `/reports/[id]`)*
> 
> Nah, kita sekarang masuk ke halaman khusus detail laporan.
> Di sebelah kiri, ada foto bukti resolusi tinggi yang bisa kita klik buat buka preview full-screen, hasil telemetri AI MobileNetV2, koordinat GPS yang ada link langsung ke Google Maps, serta info warga pelapor.
> 
> Di sebelah kanan, ada konsol triase buat admin. Di sini status machine-nya jelas:
> Admin bisa milih apakah mau:
> 1. **Tugaskan Armada Lapangan**,
> 2. **Tandai Selesai Ditangani**, atau
> 3. **Tolak Laporan** kalau fotonya buram atau bukan sampah.
> 
> Kita juga sediakan *Quick Notes Preset*, jadi admin nggak perlu ngetik manual kalau lagi buru-buru.
> Misalnya kita pilih: *'Truk DLH ditugaskan menuju titik koordinat'*, lalu klik **Simpan Perubahan Status**.
> 
> *(Aksi: Klik tombol simpan status)*
> 
> Status langsung berubah jadi *'Sedang Ditangani'*. Dan kalau kita scroll ke bawah, ada **Audit Trail** yang mencatat histori lengkap: siapa yang ngubah, jam berapa, dan apa catatannya, sehingga setiap tindakan petugas bisa dipertanggungjawabkan."

---

### [03:45 - 04:30] Backend & Arsitektur Cloud

*(Aksi: Buka tab Swagger `/docs` di Railway)*

> "Sedikit membahas sisi teknis backend:
> 
> Service backend ini kita bangun pakai **FastAPI** dan udah live di Railway.
> - Menggunakan autentikasi JWT dengan Role-Based Access Control (RBAC) buat misahin hak akses Admin dan Warga.
> - Menggunakan arsitektur database adaptif: default-nya support PostgreSQL, tapi punya fallback otomatis ke SQLite buat local dev atau recovery.
> - Endpoint inferensi `/api/v1/predict` jalan sangat cepat (<100ms) berkat optimasi bobot model MobileNetV2.
> - Kode-kode ini juga sudah lolos puluhan unit test dan integration test otomatis."

---

### [04:30 - 05:00] Closing: Penutup yang Mantap

*(Aksi: Kembali ke halaman utama Web SWMS)*

> "Kurang lebih seperti itu alur kerja Smart Waste Management System.
> Mulai dari aplikasi mobile yang ramah warga, inferensi AI yang otomatis, web dashboard yang rapi buat operasional dinas, sampai backend cloud yang stabil dan siap pakai 24/7.
> 
> Semua source code, dokumentasi API, diagram arsitektur, dan file APK release sudah saya sertakan lengkap di repositori GitHub.
> 
> Sekian demo dari saya. Terima kasih banyak atas waktu dan kesempatan dari tim Bilcode Technology, dan saya siap untuk diskusi teknis lebih lanjut. Sampai jumpa!"
