'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  MapPin,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  Activity,
  Layers,
  FileText,
  Users,
  Compass,
  ExternalLink,
  Cpu,
  Clock,
  Radio,
  Truck,
  Camera,
  Check,
} from 'lucide-react';
import Logo from '@/components/Logo';
import AboutBento from '@/components/ui/about-bento';
import ResponsiveHeroBanner from '@/components/ResponsiveHeroBanner';

export default function LandingPage() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [userRole, setUserRole] = useState<string>('guest');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      const userStr = localStorage.getItem('user');
      if (token && userStr) {
        setIsAuthenticated(true);
        try {
          const u = JSON.parse(userStr);
          setUserRole(u.role || 'user');
        } catch (_) {}
      }
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans selection:bg-emerald-600 selection:text-white">
      {/* 21st.dev Responsive Hero Banner adapted with Inter Font & Eco-Tech Emerald Palette */}
      <ResponsiveHeroBanner
        badgeLabel="BARU v1.0"
        badgeText="AI MobileNetV2 Vision & GPS Geotagging 2026"
        title="Akselerasi Keberlanjutan Kota"
        titleLine2="dengan AI Vision & Geotagging"
        description="SWMS menghubungkan pelaporan foto bukti warga, inferensi AI MobileNetV2 berkecepatan tinggi, serta orkestrasi armada kebersihan lapangan secara waktu-nyata tanpa kehilangan data."
        primaryButtonText="Akses Dashboard Operasional"
        primaryButtonHref="/dashboard"
        secondaryButtonText="Tinjau Laporan Sampah"
        secondaryButtonHref="/reports"
        isAuthenticated={isAuthenticated}
      />

      {/* Live Command Center Preview Section */}
      <section className="py-16 sm:py-20 bg-slate-900 text-white border-b border-slate-800 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-10">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full">
              Pusat Komando Terpadu
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight mt-3">
              Telemetri Laporan Waktu-Nyata
            </h2>
            <p className="text-slate-400 text-sm sm:text-base mt-2">
              Setiap laporan warga diproses seketika dengan penandaan koordinat satelit dan validasi akurasi AI.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="rounded-3xl border border-slate-800 bg-slate-950 p-5 sm:p-7 shadow-2xl shadow-slate-950/40 relative overflow-hidden">
              {/* Header Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-800 gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="font-mono text-xs font-semibold text-slate-300">
                    SWMS LIVE TELEMETRY CONSOLE • KOTA JAKARTA PUSAT
                  </span>
                </div>
                <div className="flex items-center gap-2 self-start sm:self-auto font-mono text-[11px] text-slate-400">
                  <span className="bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-emerald-400">
                    API 200 OK
                  </span>
                  <span>LATENSI: 78ms</span>
                </div>
              </div>

              {/* Simulated Live Report Stream Row */}
              <div className="mt-5 grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                {/* Visual Report Card */}
                <div className="md:col-span-7 bg-slate-900/90 rounded-2xl border border-slate-800 p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-slate-400">#RPT-2026-08819</span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 text-xs font-bold">
                      <Truck className="h-3 w-3" />
                      Sedang Ditangani
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-sm sm:text-base text-white">
                      Tumpukan Botol Plastik &amp; Kemasan di Saluran Air
                    </h3>
                    <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                      <MapPin className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                      <span>Jl. Jend. Sudirman Kav 21, Jakarta Pusat (-6.208763, 106.845598)</span>
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80">
                    <span className="inline-flex items-center gap-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2.5 py-1 rounded-lg text-xs font-semibold">
                      <Cpu className="h-3 w-3" />
                      AI: Plastic Waste (97.4%)
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      MobileNetV2 Inferred &lt;100ms
                    </span>
                  </div>
                </div>

                {/* Dispatch & Metric Summary Panel */}
                <div className="md:col-span-5 grid grid-cols-2 gap-3">
                  <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-3.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Armada DLH</span>
                    <span className="text-base font-extrabold text-white mt-1 block">Truck #04</span>
                    <span className="text-[11px] text-emerald-400 mt-0.5 block">En Route (3 Menit)</span>
                  </div>
                  <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-3.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Status Validasi</span>
                    <span className="text-base font-extrabold text-white mt-1 block">Diverifikasi</span>
                    <span className="text-[11px] text-slate-400 mt-0.5 block">Audit Trail Recorded</span>
                  </div>
                  <div className="col-span-2 bg-emerald-950/40 rounded-2xl border border-emerald-900/50 p-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                      <span className="text-xs text-emerald-200 font-medium">Auto Reverse Geocoding Selesai</span>
                    </div>
                    <span className="font-mono text-[10px] text-emerald-400 bg-emerald-900/60 px-2 py-0.5 rounded">
                      GPS LOCKED
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3 Core Architecture Pillars Section */}
      <section className="py-16 sm:py-20 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 bg-emerald-100 border border-emerald-200 px-3 py-1 rounded-full">
              Fitur Arsitektur Utama
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mt-3">
              Solusi Terpadu Hulu ke Hilir
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mt-2">
              Tiga pilar teknologi yang memastikan setiap laporan tertangani secara akurat dan transparan.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Pillar 1 */}
            <div className="rounded-3xl border border-slate-200 bg-white p-7 shadow-xs hover:border-slate-300 hover:shadow-md transition-all">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-600 text-white mb-5 shadow-md shadow-emerald-600/20">
                <Sparkles className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-extrabold text-slate-900 tracking-tight">
                AI Vision MobileNetV2
              </h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed font-normal">
                Klasifikasi citra sampah otomatis dalam &lt;100ms dengan akurasi &gt;85% untuk tiga kategori standar: Organik, Plastik, dan Kertas.
              </p>
              <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-semibold">
                <span>Transfer Learning</span>
                <span className="text-emerald-700 font-bold">150+ Dataset</span>
              </div>
            </div>

            {/* Pillar 2 */}
            <div className="rounded-3xl border border-slate-200 bg-white p-7 shadow-xs hover:border-slate-300 hover:shadow-md transition-all">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white mb-5 shadow-md shadow-slate-900/20">
                <MapPin className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-extrabold text-slate-900 tracking-tight">
                Geotagging &amp; Mini-Map
              </h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed font-normal">
                Koordinat GPS satelit terkunci otomatis dari kamera ponsel dan divisualisasikan langsung melalui peta interaktif OpenStreetMap pada modal tinjau.
              </p>
              <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-semibold">
                <span>Akurasi Satelit</span>
                <span className="text-slate-900 font-bold">OpenStreetMap</span>
              </div>
            </div>

            {/* Pillar 3 */}
            <div className="rounded-3xl border border-slate-200 bg-white p-7 shadow-xs hover:border-slate-300 hover:shadow-md transition-all">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-600 text-white mb-5 shadow-md shadow-emerald-600/20">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-extrabold text-slate-900 tracking-tight">
                Audit Trail Tanpa Data Loss
              </h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed font-normal">
                Tiap disposisi status dari Pending, In Progress, hingga Completed tersimpan secara permanen dalam riwayat audit lengkap dengan catatan validator.
              </p>
              <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-semibold">
                <span>Relational Integrity</span>
                <span className="text-emerald-700 font-bold">Ekspor CSV 1-Klik</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3 Waste Categories Section: Required by Bilcode Spec */}
      <section className="py-16 sm:py-20 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 bg-slate-100 border border-slate-200 px-3 py-1 rounded-full">
              Spesifikasi Model AI
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mt-3">
              3 Kategori Klasifikasi Sampah
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mt-2">
              Model dilatih untuk membedakan sampah dengan presisi tinggi demi mempercepat pemilahan di TPA.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Category 1: Organic */}
            <div className="rounded-3xl border border-emerald-200 bg-emerald-50/40 p-6 flex flex-col justify-between">
              <div>
                <div className="inline-flex px-3 py-1 rounded-full bg-emerald-600 text-white text-xs font-bold uppercase tracking-wide mb-4">
                  Kategori 01
                </div>
                <h3 className="text-xl font-bold text-slate-900">Organic Waste</h3>
                <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                  Sisa makanan, potongan sayur, kulit buah, dan daun gugur. Diprioritaskan untuk fasilitas komposting dan biogas kota.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-emerald-200/80 flex items-center justify-between text-xs font-semibold text-emerald-800">
                <span>Waktu Dekomposisi</span>
                <span className="font-bold">2 - 6 Minggu</span>
              </div>
            </div>

            {/* Category 2: Plastic */}
            <div className="rounded-3xl border border-slate-200 bg-white p-6 flex flex-col justify-between shadow-xs">
              <div>
                <div className="inline-flex px-3 py-1 rounded-full bg-blue-600 text-white text-xs font-bold uppercase tracking-wide mb-4">
                  Kategori 02
                </div>
                <h3 className="text-xl font-bold text-slate-900">Plastic Waste</h3>
                <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                  Botol plastik PET, kantong kresek, kemasan sachet, dan gelas plastik. Disalurkan ke bank sampah dan industri daur ulang polimer.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-slate-600">
                <span>Potensi Daur Ulang</span>
                <span className="font-bold text-slate-900">Tinggi (Sirkular)</span>
              </div>
            </div>

            {/* Category 3: Paper */}
            <div className="rounded-3xl border border-slate-200 bg-white p-6 flex flex-col justify-between shadow-xs">
              <div>
                <div className="inline-flex px-3 py-1 rounded-full bg-amber-600 text-white text-xs font-bold uppercase tracking-wide mb-4">
                  Kategori 03
                </div>
                <h3 className="text-xl font-bold text-slate-900">Paper Waste</h3>
                <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                  Kardus karton, kertas dokumen, majalah, dan koran bekas. Dipilah untuk pengolahan bubur kertas (pulp) ramah lingkungan.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-slate-600">
                <span>Nilai Pemilahan</span>
                <span className="font-bold text-slate-900">Ekonomis Cepat</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Bento Section (Impact & Metrics with Unified Color) */}
      <AboutBento />

      {/* Municipal Metric Counters Strip */}
      <section className="border-y border-slate-200 bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div className="p-6 rounded-2xl border border-slate-200/80 bg-slate-50/70">
              <div className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">96.8%</div>
              <div className="mt-1.5 text-xs sm:text-sm text-slate-500 font-semibold">Akurasi Model AI</div>
            </div>
            <div className="p-6 rounded-2xl border border-slate-200/80 bg-slate-50/70">
              <div className="text-3xl sm:text-4xl font-black text-emerald-700 tracking-tight">&lt; 100ms</div>
              <div className="mt-1.5 text-xs sm:text-sm text-slate-500 font-semibold">Waktu Inferensi Edge</div>
            </div>
            <div className="p-6 rounded-2xl border border-slate-200/80 bg-slate-50/70">
              <div className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">100%</div>
              <div className="mt-1.5 text-xs sm:text-sm text-slate-500 font-semibold">Integritas Audit Trail</div>
            </div>
            <div className="p-6 rounded-2xl border border-slate-200/80 bg-slate-50/70">
              <div className="text-3xl sm:text-4xl font-black text-emerald-700 tracking-tight">WIB (UTC+7)</div>
              <div className="mt-1.5 text-xs sm:text-sm text-slate-500 font-semibold">Sinkronisasi Real-Time</div>
            </div>
          </div>
        </div>
      </section>

      {/* Pre-Footer Call to Action Banner */}
      <section className="py-16 bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            Siap Mengoptimalkan Pengelolaan Sampah Kota Anda?
          </h2>
          <p className="text-slate-300 text-sm sm:text-base max-w-xl mx-auto font-normal">
            Akses dashboard operasional untuk memantau sebaran timbulan sampah dan kelola armada lapangan secara waktu-nyata.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3.5 pt-2">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 text-sm font-bold text-white hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-600/20 active:scale-[0.98]"
            >
              <span>Masuk Portal SWMS</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-6 py-3 text-sm font-bold text-slate-200 hover:bg-slate-700 hover:text-white transition-all shadow-xs"
            >
              <span>Dokumentasi API Swagger</span>
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 bg-slate-950 text-slate-400 text-xs border-t border-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <Logo size={28} showText={true} variant="inverted" />
            <span className="text-slate-700">|</span>
            <span className="text-slate-400 font-medium">PT Bilcode Teknologi Indonesia</span>
          </div>
          <div className="flex items-center gap-5">
            <Link href="/dashboard" className="hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link href="/reports" className="hover:text-white transition-colors">
              Laporan Sampah
            </Link>
            <Link href="/login" className="hover:text-white transition-colors">
              Masuk Portal
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-emerald-400 transition-colors inline-flex items-center gap-1 font-semibold"
            >
              <span>API Docs</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
