# Architectural Decision Records (ADR)
## Smart Waste Management System (SWMS)

> Format pencatatan keputusan arsitektural berbasis **MADR (Markdown Architectural Decision Records)**.

---

### ADR-001: Unified FastAPI Service untuk Backend Bisnis dan Inferensi AI
* **Status:** Diterima (*Accepted*)
* **Konteks:** Brief technical test mewajibkan pembuatan backend REST API dan model Machine Learning berbasis Python dengan endpoint inferensi FastAPI. Kandidat memiliki batas waktu 5 hari kalender.
* **Opsi yang Dipertimbangkan:**
  1. *Opsi Microservice Terpisah:* Laravel untuk bisnis API + FastAPI untuk AI inference.
  2. *Opsi Unified Monolith:* FastAPI untuk seluruh bisnis API (Auth, CRUD, Dashboard) sekaligus melayani inferensi AI secara in-memory.
* **Keputusan:** Memilih **Opsi 2 (Unified FastAPI)**.
* **Konsekuensi & Rationale:**
  * **Positif:** Mengurangi beban maintenance server dari 2 menjadi 1. Menghilangkan latency HTTP antar-server saat inferensi. Dokumentasi Swagger UI `/docs` otomatis ter-generate secara utuh dalam satu portal.
  * **Negatif:** Python concurrency berbasis asyncio memerlukan perhatian khusus saat menangani inferensi PyTorch berbasis CPU (dimitigasi dengan menjalankan inferensi via `torch.no_grad()` dan offloading ke threadpool jika diperlukan).

---

### ADR-002: Pemilihan MobileNetV2 untuk Klasifikasi Sampah
* **Status:** Diterima (*Accepted*)
* **Konteks:** Model ML harus mengklasifikasikan 3 kategori sampah (Organik, Plastik, Kertas) dengan dataset $\ge 150$ gambar dan target akurasi testing $\ge 80\%$. Inferensi harus responsif pada lingkungan cloud CPU murah/gratis.
* **Opsi yang Dipertimbangkan:**
  1. *Custom CNN dari nol (Scratch)*: Risiko overfitting tinggi pada dataset kecil ($\approx 200$ sampel).
  2. *ResNet-50 / DenseNet*: Akurasi tinggi namun ukuran file model besar ($>100\text{ MB}$) dan lambat di CPU.
  3. *MobileNetV2 (Pre-trained ImageNet)*: Sangat ringan ($\approx 14\text{ MB}$), cepat di CPU, akurasi tinggi berkat Transfer Learning.
* **Keputusan:** Memilih **MobileNetV2 (Transfer Learning)**.
* **Konsekuensi & Rationale:**
  * Dengan fine-tuning layer klasifikasi akhir dan augmentasi data, model dengan mudah mencapai akurasi $>85\%$ hanya dalam 10-15 epoch, ukuran model kecil, dan waktu inferensi $<200\text{ ms}$ di CPU.

---

### ADR-003: Tipografi Kombinasi Space Grotesk + Inter
* **Status:** Diterima (*Accepted*)
* **Konteks:** Sistem membutuhkan identitas visual yang profesional, berkarakter modern (Smart City tech-forward), namun tetap memiliki legibilitas data tabel yang sempurna tanpa kesan kaku.
* **Keputusan:** Menggunakan **Space Grotesk** untuk display/heading dan **Inter** untuk body copy serta tabel data, dipadukan dengan **JetBrains Mono** untuk data koordinat GPS.
* **Konsekuensi & Rationale:**
  * `Space Grotesk` memberikan karakter inovatif dan tegas pada dashboard analitik.
  * `Inter` adalah standar emas web industri untuk membaca deretan angka, formulir, dan status badges.

---

### ADR-004: Skema Database Relasional PostgreSQL dengan Audit Trail
* **Status:** Diterima (*Accepted*)
* **Konteks:** Laporan sampah memiliki siklus hidup status (`Pending` $\rightarrow$ `In Progress` $\rightarrow$ `Completed` / `Rejected`). Penguji menilai integritas skema database (Bobot 5%).
* **Keputusan:** Memisahkan tabel utama `waste_reports` dengan tabel riwayat `report_logs`.
* **Konsekuensi & Rationale:**
  * Menjamin setiap perubahan status memiliki riwayat yang tidak dapat dimanipulasi (*tamper-proof*), mencatat siapa admin yang menyetujui, waktu eksekusi, dan catatan lapangan.
