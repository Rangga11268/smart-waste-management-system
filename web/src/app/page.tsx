'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  MapPin,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  Zap,
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
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col selection:bg-emerald-500 selection:text-white">
      {/* Top Floating Glass Navigation */}
      <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-900/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center group">
              <Logo size={40} showText={true} />
            </Link>
            <span className="hidden md:inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-0.5 text-xs font-semibold text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Sistem Operasional Aktif (WIB)
            </span>
          </div>

          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 text-sm font-bold text-slate-950 hover:bg-emerald-400 transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)] active:scale-[0.98]"
              >
                <span>Buka Dashboard</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  className="rounded-xl border border-slate-700/80 bg-slate-800/60 px-4 py-2.5 text-xs sm:text-sm font-semibold text-slate-200 hover:bg-slate-700 hover:text-white transition-all"
                >
                  Masuk Portal
                </Link>
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-500 px-4 py-2.5 text-xs sm:text-sm font-bold text-slate-950 hover:bg-emerald-400 transition-all shadow-[0_0_20px_rgba(16,185,129,0.25)] active:scale-[0.98]"
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
      <section className="relative pt-16 pb-24 lg:pt-24 lg:pb-32 overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(16,185,129,0.15),transparent)] pointer-events-none" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-950/60 px-4 py-1.5 text-xs font-bold text-emerald-300 backdrop-blur-sm">
              <Sparkles className="h-4 w-4 text-emerald-400" />
              <span>Smart Waste Management System (SWMS)</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight font-heading">
              Akselerasi Pengelolaan Sampah Kota Berbasis <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">Computer Vision</span>.
            </h1>

            <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-sans max-w-2xl mx-auto">
              Platform modern yang memadukan inferensi AI MobileNetV2 berkecepatan &lt;100ms, geocoding alamat terbalik otomatis, dan koordinasi armada secara real-time.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-6 py-3.5 text-sm sm:text-base font-bold text-slate-950 shadow-[0_0_30px_rgba(16,185,129,0.35)] hover:bg-emerald-400 active:scale-[0.98] transition-all"
              >
                <span>Akses Dashboard Operasional</span>
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                href="/reports"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/80 px-6 py-3.5 text-sm sm:text-base font-semibold text-white hover:bg-slate-700 hover:border-slate-600 active:scale-[0.98] transition-all"
              >
                <span>Daftar Laporan Publik</span>
              </Link>
            </div>
          </div>

          {/* Interactive Feature Showcase Matrix */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-xs hover:border-emerald-500/50 transition-all group">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-5 group-hover:scale-110 transition-transform">
                <Sparkles className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white font-heading">
                AI MobileNetV2 Otomatis
              </h3>
              <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                Klasifikasi citra sampah instan ke 3 kategori (Organik, Plastik, Kertas) dengan visual confidence meter dan 1-tap chip correction.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-xs hover:border-emerald-500/50 transition-all group">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-5 group-hover:scale-110 transition-transform">
                <MapPin className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white font-heading">
                Reverse Geocoding Presisi
              </h3>
              <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                Mengonversi koordinat GNSS secara otomatis menjadi alamat jalan, kelurahan, dan kota nyata sehingga petugas langsung mengenali titik jemput.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-xs hover:border-emerald-500/50 transition-all group">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-5 group-hover:scale-110 transition-transform">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-white font-heading">
                Audit Trail Terpadu
              </h3>
              <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                Pencatatan transisi status (Pending &rarr; In Progress &rarr; Completed) dengan audit log waktu-nyata tanpa kehilangan data.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Metrics Strip */}
      <section className="border-b border-slate-800 bg-slate-950 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl sm:text-4xl font-extrabold text-white font-heading">96.8%</div>
              <div className="mt-1 text-xs text-slate-400 uppercase tracking-wider font-semibold">
                Akurasi Model AI
              </div>
            </div>
            <div>
              <div className="text-3xl sm:text-4xl font-extrabold text-emerald-400 font-heading">&lt; 100ms</div>
              <div className="mt-1 text-xs text-slate-400 uppercase tracking-wider font-semibold">
                Kecepatan Inferensi
              </div>
            </div>
            <div>
              <div className="text-3xl sm:text-4xl font-extrabold text-white font-heading">100%</div>
              <div className="mt-1 text-xs text-slate-400 uppercase tracking-wider font-semibold">
                Integritas Audit Data
              </div>
            </div>
            <div>
              <div className="text-3xl sm:text-4xl font-extrabold text-emerald-400 font-heading">24/7</div>
              <div className="mt-1 text-xs text-slate-400 uppercase tracking-wider font-semibold">
                Sinkronisasi Lapangan
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-slate-800 bg-slate-950 text-slate-500 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-300">SWMS Enterprise</span>
            <span>&bull;</span>
            <span>PT Bilcode Teknologi Indonesia</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="hover:text-slate-300 transition-colors">
              Dashboard
            </Link>
            <Link href="/reports" className="hover:text-slate-300 transition-colors">
              Laporan Sampah
            </Link>
            <Link href="/login" className="hover:text-slate-300 transition-colors">
              Masuk
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-emerald-400 transition-colors inline-flex items-center gap-1"
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
