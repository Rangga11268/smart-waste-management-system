# Smart Waste Management System (SWMS) — UI/UX & Styling Guide

> **Design Philosophy: Clean, Modern, Purpose-Driven (Anti-Slop)**
> Aplikasi pengelolaan sampah perkotaan harus terasa tangguh, bersih, kredibel, dan sangat mudah digunakan oleh petugas lapangan maupun warga biasa di bawah sinar matahari langsung (kontras tinggi, target sentuh nyaman).

---

## 1. Color Palette (Eco-Tech High-Contrast Theme)

Palet warna didesain dengan konsep **"Eco-Tech Resilience"**: dominasi hijau emerald modern untuk merepresentasikan keberlanjutan dan kebersihan lingkungan, dipadukan dengan neutral slate/zinc untuk tampilan software enterprise yang matang.

### Primary & Brand Colors
| Token Name | Hex Code | Tailwind Class | Penggunaan |
| :--- | :--- | :--- | :--- |
| `primary-50` | `#ecfdf5` | `bg-emerald-50` | Background highlight, subtle active state |
| `primary-500`| `#10b981` | `bg-emerald-500` | Accents, floating badges |
| `primary-600`| `#059669` | `bg-emerald-600` | **Brand Primary**, tombol utama, active nav |
| `primary-700`| `#047857` | `bg-emerald-700` | Hover states pada tombol utama |
| `primary-900`| `#064e3b` | `bg-emerald-900` | Header text emphasis, dark accents |

### Neutral Base (Slate & Zinc)
| Token Name | Hex Code | Tailwind Class | Penggunaan |
| :--- | :--- | :--- | :--- |
| `surface-ground`| `#f8fafc` | `bg-slate-50` | Background canvas aplikasi web & mobile |
| `surface-card`  | `#ffffff` | `bg-white` | Card container, modal, popup |
| `border-subtle` | `#e2e8f0` | `border-slate-200` | Card borders, table dividers, inputs |
| `text-muted`    | `#64748b` | `text-slate-500` | Label bantuan, timestamp, metadata |
| `text-body`     | `#334155` | `text-slate-700` | Paragraf reguler, isi tabel |
| `text-heading`  | `#0f172a` | `text-slate-900` | Judul, angka metrik statistik, heading |

### Status Badges (Semantic Indicators)
*Sangat penting untuk diferensiasi status laporan sampah di Web & Mobile:*

| Status | Badge Background | Badge Text | Border | Makna Operasional |
| :--- | :--- | :--- | :--- | :--- |
| **`Pending`** | `bg-amber-50` | `text-amber-700` | `border-amber-200` | Laporan baru masuk dari warga, belum diverifikasi. |
| **`In Progress`** | `bg-blue-50` | `text-blue-700` | `border-blue-200` | Petugas armada kebersihan sedang menuju lokasi. |
| **`Completed`** | `bg-emerald-50` | `text-emerald-700` | `border-emerald-200`| Sampah sudah diangkut & lokasi dibersihkan. |
| **`Rejected`** | `bg-rose-50` | `text-rose-700` | `border-rose-200` | Laporan palsu, duplikat, atau foto tidak valid. |

### AI Classification Categories (Kategori Sampah)
| Kategori | Accent Color | Hex | Badge Class |
| :--- | :--- | :--- | :--- |
| **Organic Waste** | Forest Emerald | `#16a34a` | `bg-green-100 text-green-800` |
| **Plastic Waste** | Ocean Cyan / Blue | `#0284c7` | `bg-sky-100 text-sky-800` |
| **Paper Waste** | Warm Amber / Wood | `#d97706` | `bg-amber-100 text-amber-800` |

---

## 2. Typography Hierarchy (Pilihan 1: Space Grotesk + Inter)

* **Heading & Display Font:** `Space Grotesk` (Geometric sans-serif berkarakter tajam, modern, dan bernuansa tech-forward untuk aplikasi Smart City).
* **Body, UI & Table Font:** `Inter` (Neo-grotesque kelas dunia dengan legibilitas angka dan form data yang tak tertandingi).
* **Monospace Font:** `JetBrains Mono` (Untuk koordinat GPS `lat, long`, ID Laporan `#RPT-XXXX`, dan metrik akurasi AI `94.2%`).

### Scale & Weight
* **Display / Big Stats:** `font-['Space_Grotesk'] text-3xl font-bold tracking-tight text-slate-900`
* **Page Title (H1):** `font-['Space_Grotesk'] text-2xl font-bold text-slate-900`
* **Section Title (H2):** `font-['Space_Grotesk'] text-lg font-semibold text-slate-800`
* **Card Title / Subheading:** `font-['Inter'] text-sm font-medium text-slate-600`
* **Body / Table Cell:** `font-['Inter'] text-sm font-normal text-slate-700`
* **Data Code / Coordinates:** `font-mono text-xs font-medium text-slate-500`
* **Caption / Timestamp:** `text-xs font-medium text-slate-400`

---

## 3. Web Design System (Next.js + Tailwind)

### A. Layout Structure (Admin Dashboard)
1. **Sidebar Navigation**:
   * Lebar fixed `w-64`, background `bg-white`, border kanan `border-r border-slate-200`.
   * Logo SWMS hijau di bagian atas dengan badge versi.
   * Menu Navigasi:
     * 📊 *Dashboard Overview* (Statistik & Chart)
     * 📋 *Laporan Sampah* (Tabel Master CRUD)
     * 👥 *Manajemen Pengguna* (Khusus Admin)
     * ⚙️ *Pengaturan & API Docs*
2. **Top Header Bar**:
   * Breadcrumb halaman aktif.
   * Quick status server / API indicator (`🟢 Online`).
   * User avatar & info peran (*Admin* / *Operator*).
3. **Stat Cards Widget**:
   * 4 kartu metrik di baris atas:
     1. Total Laporan Masuk
     2. Laporan Perlu Validasi (`Pending`)
     3. Laporan Sedang Dikerjakan (`In Progress`)
     4. Tingkat Penyelesaian (`Completed Rate %`)
4. **Table & Filter Component**:
   * Search input dengan ikon kaca pembesar (debounce 300ms).
   * Filter dropdown status & dropdown kategori.
   * Action buttons yang jelas: *Review / Detail*, *Update Status*, *Hapus*.

---

## 4. Mobile Design System (Flutter App)

### A. Material 3 Configuration
* `useMaterial3: true`
* `ColorScheme.fromSeed(seedColor: Color(0xFF059669))`
* Scaffold background: `Color(0xFFF8FAFC)`
* AppBar: Elevation 0, Background putih, Title hitam tebal, center title.

### B. Mobile Screen Flow
1. **Login & Register**:
   * Clean card layout, input field dengan border radius `12.0`, icon prefix (email, lock).
2. **Citizen Home Dashboard**:
   * Header sapaan hangat (*"Halo, Darell!"*).
   * Hero Banner besar: Tombol CTA menonjol **"Laporkan Sampah Baru"** dengan ikon kamera besar.
   * Daftar 3 laporan terakhir dengan timeline status live.
3. **AI Camera & Report Screen**:
   * Preview foto yang baru diambil dari kamera/galeri.
   * **AI Detection Banner**: Kartu hasil inferensi real-time:
     * Label: *"Terdeteksi: Sampah Plastik"*
     * Tingkat Keyakinan: *"Confidence: 94.2%"*
   * **Auto GPS Geotag Card**:
     * Ikon pin lokasi merah + koordinat `Latitude: -6.2088, Longitude: 106.8456`.
     * Input catatan patokan lokasi (misal: "Di sebelah warung mie ayam").
   * Tombol submit: Full-width button hijau emerald dengan haptic feedback.

---

## 5. Anti-Slop & Quality Principles
* ❌ **Hindari:** Gradient neon berlebihan, efek glassmorphism murahan yang sulit dibaca, emoji berantakan di judul formal.
* ✅ **Gunakan:** Ikon SVG bersih (Lucide Icons di Web, Material Symbols di Flutter), micro-badges bersudut halus (`rounded-full` atau `rounded-md`), dan state loading skeleton yang rapi saat data di-fetch.
