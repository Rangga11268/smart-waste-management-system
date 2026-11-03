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
import AboutBento from '@/components/ui/about-bento';

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

      {/* Hero Section (Connected to Bento Style: Bold, High-Contrast & Modern) */}
      <section className="relative pt-16 pb-16 lg:pt-24 lg:pb-20 border-b border-slate-200 bg-white overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            {/* Pill Eyebrow */}
            <div className="inline-flex items-center gap-2 rounded-full border border-violet-200 bg-violet-50 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-violet-700 shadow-xs">
              <Sparkles className="h-3.5 w-3.5 text-violet-600" />
              <span>Smart Waste Management Platform</span>
            </div>

            {/* Hero Main Heading */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-slate-900 leading-[1.1]">
              Akselerasi Keberlanjutan Kota dengan <span className="bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">AI Vision</span> & <span className="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">Geotagging</span> Presisi.
            </h1>

            {/* Subtitle with High WCAG Contrast */}
            <p className="text-base sm:text-xl text-slate-700 leading-relaxed max-w-2xl mx-auto font-medium">
              SWMS menghubungkan pelaporan foto bukti warga, inferensi model MobileNetV2 berkecepatan tinggi, serta orkestrasi armada lapangan secara waktu-nyata tanpa data loss.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center justify-center gap-3.5 pt-2">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-6 py-3.5 text-sm sm:text-base font-bold text-white shadow-lg shadow-slate-950/20 hover:bg-slate-800 active:scale-[0.98] transition-all"
              >
                <span>Akses Dashboard Operasional</span>
                <ArrowRight className="h-4 w-4 text-emerald-400" />
              </Link>
              <Link
                href="/reports"
                className="inline-flex items-center gap-2 rounded-2xl border-2 border-slate-200 bg-white px-6 py-3.5 text-sm sm:text-base font-bold text-slate-700 hover:border-slate-300 hover:bg-slate-50 active:scale-[0.98] transition-all"
              >
                <span>Tinjau Laporan Sampah</span>
              </Link>
            </div>
          </div>

          {/* Quick Pillar Preview Grid */}
          <div className="mt-14 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-3xl border border-slate-200 bg-slate-50/80 p-7 hover:bg-white hover:border-slate-300 hover:shadow-md transition-all">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500 text-white mb-5 shadow-md shadow-emerald-500/20">
                <Sparkles className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-extrabold text-slate-900 tracking-tight">
                AI Vision MobileNetV2
              </h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed font-normal">
                Klasifikasi citra otomatis dalam &lt;100ms dengan akurasi 96.8% untuk kategori Organik, Plastik, dan Kertas.
              </p>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-slate-50/80 p-7 hover:bg-white hover:border-slate-300 hover:shadow-md transition-all">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-600 text-white mb-5 shadow-md shadow-violet-500/20">
                <MapPin className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-extrabold text-slate-900 tracking-tight">
                Reverse Geocoding Presisi
              </h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed font-normal">
                Koordinat GPS diubah otomatis menjadi nama jalan, kelurahan, dan kota nyata untuk rute armada lapangan.
              </p>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-slate-50/80 p-7 hover:bg-white hover:border-slate-300 hover:shadow-md transition-all">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white mb-5 shadow-md shadow-slate-900/20">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-extrabold text-slate-900 tracking-tight">
                Audit Trail Zero-Data-Loss
              </h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed font-normal">
                Tiap disposisi status tersimpan akuntabel dalam riwayat kronologis lengkap dengan catatan validator.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* About Bento Section (High-Contrast Impact Showcase) */}
      <AboutBento />

      {/* Metrics Strip */}
      <section className="border-y border-slate-200 bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div className="p-6 rounded-2xl border border-slate-200/80 bg-slate-50/60">
              <div className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">96.8%</div>
              <div className="mt-1.5 text-xs sm:text-sm text-slate-500 font-semibold">Akurasi Model AI</div>
            </div>
            <div className="p-6 rounded-2xl border border-slate-200/80 bg-slate-50/60">
              <div className="text-3xl sm:text-4xl font-black text-emerald-600 tracking-tight">&lt; 100ms</div>
              <div className="mt-1.5 text-xs sm:text-sm text-slate-500 font-semibold">Waktu Inferensi Edge</div>
            </div>
            <div className="p-6 rounded-2xl border border-slate-200/80 bg-slate-50/60">
              <div className="text-3xl sm:text-4xl font-black text-violet-600 tracking-tight">100%</div>
              <div className="mt-1.5 text-xs sm:text-sm text-slate-500 font-semibold">Integritas Audit Trail</div>
            </div>
            <div className="p-6 rounded-2xl border border-slate-200/80 bg-slate-50/60">
              <div className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">WIB (UTC+7)</div>
              <div className="mt-1.5 text-xs sm:text-sm text-slate-500 font-semibold">Sinkronisasi Waktu Nyata</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-10 bg-slate-900 text-slate-400 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <Logo size={28} showText={true} variant="inverted" />
            <span className="text-slate-600">|</span>
            <span className="text-slate-300 font-medium">PT Bilcode Teknologi Indonesia</span>
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
