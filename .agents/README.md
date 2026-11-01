# .agents — Multi-Agent Teamwork & Skills Registry
## Smart Waste Management System (SWMS) — Bilcode Technology

Direktori `.agents/` ini berfungsi sebagai pusat koordinasi agen otonom (*Autonomous Teamwork*) dan penyimpanan lokal untuk keahlian teknis (*Skills Registry*) yang digunakan selama pengembangan sistem 5 hari ini.

---

## 1. Struktur Direktori

```text
.agents/
├── skills/                     # Salinan keahlian teknis (Skills) yang digunakan dalam proyek
│   ├── using-agent-skills/     # Meta-skill pengatur workflow & discovery
│   ├── spec-driven-development/# Standar spesifikasi sebelum coding
│   ├── ...
│   └── tdd/                    # Test-driven development
│
├── teamwork/                   # Ruang kerja delegasi sub-agen & koordinasi tim
│   ├── orchestrator/           # Briefing & status gating utama
│   └── handoff/                # Ringkasan transfer state antar fase (ML -> BE -> FE -> Mobile)
│
└── README.md                   # Dokumen panduan ini
```

---

## 2. Analisis & Kurasi Skills yang Dipilih

Dari total puluhan skills yang terpasang di ekosistem Antigravity, sebanyak **26 skills** terpilih dan dikurasi secara presisi untuk kebutuhan proyek *Fullstack + Mobile + Machine Learning* ini:

### A. Lifecycle, Specification & Task Planning (Pondasi Proyek)
1. **`using-agent-skills`**: Meta-skill untuk navigasi fase pengembangan dan aturan non-negosiabel (surface assumptions, push back bila over-engineered).
2. **`spec-driven-development`**: Menjamin semua fitur memiliki kriteria sukses terukur sebelum kode ditulis.
3. **`planning-and-task-breakdown`**: Memecah roadmap 5 hari menjadi tugas vertikal kecil yang bisa diverifikasi secara independen.
4. **`incremental-implementation`**: Menghindari perubahan raksasa yang rentan error dengan mengimplementasikan irisan tipis (*thin vertical slices*).
5. **`ponytail`**: Prinsip *lazy senior developer* (YAGNI, minimalkan dependensi, pakai utilitas yang sudah ada, diff terpendek yang bekerja).
6. **`superpowers`**: Framework eksekusi agen terstruktur dan verifikasi sebelum tugas dinyatakan selesai.

### B. UI/UX, Design Tokens & Anti-Slop (Kualitas Tampilan Web & Mobile)
7. **`frontend-ui-engineering`**: Membangun tampilan web Next.js yang standar industri, responsif, dan aksesibel.
8. **`antislop` & `antislop-ui`**: Menghilangkan desain generik murahan AI; memastikan hirarki visual bersih, kontras tinggi, dan tata letak bermakna.
9. **`antislop-code`**: Menjaga kebersihan komentar kode agar tidak tercemar boilerplate AI slop.
10. **`antislop-layoutmobile`**: Mengoptimalkan layout responsif, area tap sentuhan jempol di smartphone, dan scroll aman.
11. **`antislop-human`**: Standar kontras warna teks dan elemen UI agar mudah dibaca di bawah sinar matahari langsung.
12. **`design-system`**: Standar arsitektur token (warna semantic status: *Pending, In Progress, Completed, Rejected*).

### C. Backend, REST API & Database Architecture
13. **`api-and-interface-design`**: Desain antarmuka REST API yang stabil, prediktif, dan error-handling konsisten.
14. **`openapi-and-api-specs`**: Kontrak OpenAPI/Swagger otomatis di FastAPI untuk memenuhi Deliverable #4.
15. **`database-design-and-migrations`**: Skema relasional PostgreSQL, indexing tabel `waste_reports` dan `users`, serta integritas foreign key.

### D. Mobile Client Development (Flutter & Dart)
16. **`flutter-architecture-and-state`**: Arsitektur berlapis Flutter (UI $\rightarrow$ Service/Logic $\rightarrow$ API) yang bersih dan bebas *memory leak*.
17. **`material-design-3-ui`**: Desain visual Flutter Material 3 berbasis seed color emerald hijau.
18. **`flutter-build-responsive-layout`**: Layout Flutter adaptif untuk berbagai resolusi layar smartphone.
19. **`flutter-use-http-package`**: Konsumsi REST API dan pengiriman file gambar multipart (bukti foto sampah + inferensi AI).

### E. Quality Assurance, Security & Debugging
20. **`tdd`**: Pembuatan unit test pada modul otentikasi JWT dan kalkulasi laporan sampah.
21. **`debugging-and-error-recovery`**: Pendekatan sistematis pelacakan *root cause* jika terjadi kendala runtime.
22. **`code-review`**: Tinjauan kode dua arah (Kesesuaian Standar & Kesesuaian Spesifikasi Bilcode).
23. **`security-and-hardening`**: Proteksi kata sandi dengan bcrypt, token expiration, dan sanitasi input form.

### F. Git Workflow & Final Deliverables
24. **`git-workflow-and-versioning`**: Manajemen commit Git atomik yang rapi di GitHub.
25. **`documentation-and-adrs`**: Penyusunan dokumentasi arsitektur, diagram alur, dan panduan setup `README.md`.
