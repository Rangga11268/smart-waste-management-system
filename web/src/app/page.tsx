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
} from 'lucide-react';
import Logo from '@/components/Logo';

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
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 border-b border-slate-200/90 bg-white/95 backdrop-blur-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center group">
              <Logo size={36} showText={true} />
            </Link>
            <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-800">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse" />
              Sistem Operasional Aktif (WIB)
            </span>
          </div>

          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-xs sm:text-sm font-semibold text-white hover:bg-emerald-700 transition-all shadow-xs active:scale-[0.98]"
              >
                <span>Buka Dashboard</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  className="rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs sm:text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-all"
                >
                  Masuk Portal
                </Link>
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 text-xs sm:text-sm font-semibold text-white hover:bg-emerald-700 transition-all shadow-xs active:scale-[0.98]"
                >
                  <span>Mulai Evaluasi</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-12 pb-16 lg:pt-20 lg:pb-24 border-b border-slate-200/90 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto space-y-5">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3.5 py-1 text-xs font-semibold text-emerald-800">
              <Sparkles className="h-3.5 w-3.5 text-emerald-600" />
              <span>Smart Waste Management System (SWMS)</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
              Pengelolaan Sampah Perkotaan Lebih Terarah dengan AI & Geotagging Presisi.
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto">
              Platform kota terintegrasi yang menghubungkan formulir bukti warga, model klasifikasi MobileNetV2, dan koordinasi armada lapangan secara waktu-nyata.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-3 pt-3">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white shadow-xs hover:bg-emerald-700 active:scale-[0.98] transition-all"
              >
                <span>Akses Dashboard Operasional</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/reports"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 active:scale-[0.98] transition-all"
              >
                <span>Tinjau Laporan Sampah</span>
              </Link>
            </div>
          </div>

          {/* Core Feature Matrix */}
          <div className="mt-14 grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-6 hover:bg-white hover:border-slate-300 transition-all">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100 text-emerald-800 mb-4 font-bold">
                <Sparkles className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900">
                Deteksi Otomatis MobileNetV2
              </h3>
              <p className="mt-2 text-xs sm:text-sm text-slate-600 leading-relaxed">
                Inferensi gambar sampah langsung ke 3 kategori utama (Organik, Plastik, Kertas) dengan meteran keyakinan serta koreksi 1-ketuk bagi warga.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-6 hover:bg-white hover:border-slate-300 transition-all">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100 text-emerald-800 mb-4 font-bold">
                <MapPin className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900">
                Reverse Geocoding Presisi
              </h3>
              <p className="mt-2 text-xs sm:text-sm text-slate-600 leading-relaxed">
                Koordinat GPS diubah secara otomatis menjadi alamat jalan, kelurahan, dan kota nyata agar petugas dan armada langsung mengenali lokasi penjemputan.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-6 hover:bg-white hover:border-slate-300 transition-all">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100 text-emerald-800 mb-4 font-bold">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900">
                Audit Trail Zero-Data-Loss
              </h3>
              <p className="mt-2 text-xs sm:text-sm text-slate-600 leading-relaxed">
                Tiap peralihan status (Pending &rarr; In Progress &rarr; Completed) tersimpan dalam log audit kronologis yang transparan dan akuntabel.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Metrics Strip */}
      <section className="border-b border-slate-200 bg-white py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
              <div className="text-2xl sm:text-3xl font-extrabold text-slate-900">96.8%</div>
              <div className="mt-1 text-xs text-slate-500 font-medium">Akurasi Model AI</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
              <div className="text-2xl sm:text-3xl font-extrabold text-emerald-700">&lt; 100ms</div>
              <div className="mt-1 text-xs text-slate-500 font-medium">Waktu Inferensi</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
              <div className="text-2xl sm:text-3xl font-extrabold text-slate-900">100%</div>
              <div className="mt-1 text-xs text-slate-500 font-medium">Integritas Riwayat Audit</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
              <div className="text-2xl sm:text-3xl font-extrabold text-emerald-700">WIB (UTC+7)</div>
              <div className="mt-1 text-xs text-slate-500 font-medium">Sinkronisasi Waktu Nyata</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 bg-slate-100 border-t border-slate-200 text-slate-500 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700">SWMS Enterprise</span>
            <span>&bull;</span>
            <span>PT Bilcode Teknologi Indonesia</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="hover:text-slate-800 transition-colors">
              Dashboard
            </Link>
            <Link href="/reports" className="hover:text-slate-800 transition-colors">
              Laporan Sampah
            </Link>
            <Link href="/login" className="hover:text-slate-800 transition-colors">
              Masuk
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-emerald-700 transition-colors inline-flex items-center gap-1"
            >
              <span>FastAPI Docs</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
