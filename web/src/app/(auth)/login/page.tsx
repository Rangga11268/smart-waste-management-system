'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  AlertCircle,
  Loader2,
  ShieldCheck,
  UserCheck,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  MapPin,
  CheckCircle2,
  Cpu,
  Server,
  KeyRound,
} from 'lucide-react';
import { AuthProvider, useAuth } from '@/lib/auth';
import Logo from '@/components/Logo';
import axios from 'axios';

function LoginForm() {
  const router = useRouter();
  const { login, isAuthenticated, user, isLoading: authLoading } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<{ email?: string; password?: string }>({});
  const [activePreset, setActivePreset] = useState<'admin' | 'user' | null>(null);

  useEffect(() => {
    if (!authLoading && isAuthenticated && user) {
      router.replace('/dashboard');
    }
  }, [authLoading, isAuthenticated, user, router]);

  const validate = (): boolean => {
    const errors: { email?: string; password?: string } = {};

    if (!email.trim()) {
      errors.email = 'Alamat email wajib diisi';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errors.email = 'Format alamat email tidak valid';
    }

    if (!password) {
      errors.password = 'Kata sandi wajib diisi';
    } else if (password.length < 6) {
      errors.password = 'Kata sandi minimal 6 karakter';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await login(email.trim(), password);
      router.push('/dashboard');
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401) {
          setErrorMessage('Email atau kata sandi tidak valid. Silakan periksa kembali kredensial Anda.');
        } else if (err.response?.status === 422) {
          setErrorMessage('Format data yang dikirimkan tidak sesuai.');
        } else if (err.response?.data?.detail) {
          const detail = err.response.data.detail;
          setErrorMessage(typeof detail === 'string' ? detail : 'Terjadi kesalahan validasi.');
        } else if (err.code === 'ECONNABORTED' || !err.response) {
          setErrorMessage('Tidak dapat terhubung ke server API. Pastikan backend SWMS aktif pada port 8000.');
        } else {
          setErrorMessage('Terjadi gangguan saat memproses login. Silakan coba lagi.');
        }
      } else {
        setErrorMessage('Terjadi kesalahan tidak terduga.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickPreset = (role: 'admin' | 'user', presetEmail: string, presetPass: string) => {
    setActivePreset(role);
    setEmail(presetEmail);
    setPassword(presetPass);
    setFormErrors({});
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 lg:bg-slate-50 flex flex-col lg:grid lg:grid-cols-12 selection:bg-emerald-600 selection:text-white">
      {/* Left Brand Showcase Column (Desktop Only) */}
      <div className="hidden lg:col-span-5 lg:flex lg:flex-col lg:justify-between bg-slate-950 p-10 xl:p-12 text-white relative overflow-hidden border-r border-slate-800 isolate">
        {/* Cinematic Smart City Background */}
        <img
          src="/hero-bg.jpg"
          alt="SWMS Eco-Tech City"
          className="w-full h-full object-cover absolute inset-0 opacity-30 scale-105 pointer-events-none transition-transform duration-1000 ease-out"
        />
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-slate-950/95 via-slate-950/85 to-slate-950" />
        <div className="pointer-events-none absolute top-1/4 -left-12 w-[450px] h-[300px] bg-emerald-500/15 blur-[120px] rounded-full" />
        <div className="pointer-events-none absolute bottom-1/4 -right-12 w-[350px] h-[250px] bg-teal-500/10 blur-[120px] rounded-full" />

        {/* Top Header & Back Link */}
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <Link href="/" className="inline-flex items-center group">
              <Logo size={40} showText={true} variant="inverted" />
            </Link>

            <Link
              href="/"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-300 hover:text-white transition-all bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 backdrop-blur-md shadow-xs"
            >
              <ArrowLeft className="h-3.5 w-3.5 text-emerald-400" />
              <span>Beranda</span>
            </Link>
          </div>

          <div className="mt-12 space-y-4">
            <p className="text-xs font-bold uppercase tracking-wider text-emerald-400">
              Sistem Pengelolaan Sampah Cerdas Terintegrasi
            </p>

            <h1 className="text-3xl xl:text-4xl font-extrabold tracking-tight text-white leading-tight font-sans">
              Akselerasi Keberlanjutan Kota{' '}
              <span className="bg-gradient-to-r from-emerald-300 via-teal-200 to-emerald-400 bg-clip-text text-transparent">
                dengan AI Vision &amp; Geotagging
              </span>
            </h1>

            <p className="text-sm text-slate-300 leading-relaxed font-sans">
              SWMS menghubungkan pelaporan warga, inferensi model AI MobileNetV2 presisi tinggi, dan orkestrasi armada kebersihan lapangan dalam satu konsol operasional waktu-nyata.
            </p>
          </div>

          {/* Micro Feature Cards */}
          <div className="mt-10 space-y-3 font-sans text-xs">
            <div className="flex items-center gap-3.5 p-3 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md text-slate-200 hover:border-emerald-500/30 transition-all">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                <Cpu className="h-4 w-4" />
              </div>
              <div>
                <span className="font-bold text-white block">AI MobileNetV2 Vision Classifier</span>
                <span className="text-slate-400 text-[11px]">Klasifikasi otomatis Organik, Plastik, &amp; Kertas &lt;100ms</span>
              </div>
            </div>

            <div className="flex items-center gap-3.5 p-3 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md text-slate-200 hover:border-emerald-500/30 transition-all">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                <MapPin className="h-4 w-4" />
              </div>
              <div>
                <span className="font-bold text-white block">Geotagging &amp; Reverse Geocode OSM</span>
                <span className="text-slate-400 text-[11px]">Kunci koordinat GPS satelit dan nama jalan otomatis</span>
              </div>
            </div>

            <div className="flex items-center gap-3.5 p-3 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md text-slate-200 hover:border-emerald-500/30 transition-all">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                <CheckCircle2 className="h-4 w-4" />
              </div>
              <div>
                <span className="font-bold text-white block">Audit Trail Disposisi Tanpa Kehilangan Data</span>
                <span className="text-slate-400 text-[11px]">Riwayat status transparan, role-based access control</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom System Telemetry Indicator */}
        <div className="relative z-10 border-t border-slate-800/80 pt-6 mt-12 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2 font-mono text-[11px] text-slate-300">
                        <span>FastAPI Core 8000: ONLINE</span>
          </div>
          <span className="font-mono text-emerald-400 text-[11px]">Bilcode SWMS v1.0</span>
        </div>
      </div>

      {/* Right Login Form Column */}
      <div className="flex-1 lg:col-span-7 flex flex-col justify-center px-4 py-10 sm:px-8 lg:px-12 xl:px-16 bg-slate-50 relative">
        {/* Subtle Ambient Radial Highlight on Canvas */}
        <div className="pointer-events-none absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 blur-[120px] rounded-full" />

        <div className="mx-auto w-full max-w-md relative z-10">
          {/* Mobile Header with Logo & Back Link */}
          <div className="lg:hidden flex items-center justify-between mb-8">
            <Logo size={42} showText={true} />
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-2xs"
            >
              <ArrowLeft className="h-3.5 w-3.5 text-emerald-600" />
              <span>Beranda</span>
            </Link>
          </div>

          {/* Form Header */}
          <div className="mb-6">
            <p className="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-2">
              Portal Akses Resmi
            </p>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 font-sans">
              Masuk ke Akun Anda
            </h2>
            <p className="mt-1.5 text-sm text-slate-600 leading-relaxed">
              Masukkan kredensial akun untuk mengakses konsol triage dan dashboard operasional.
            </p>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div
              className="mb-6 flex items-start gap-3 rounded-2xl border border-rose-200 bg-rose-50/90 p-4 text-sm text-rose-800 shadow-sm animate-fade-slide-in-1"
              role="alert"
            >
              <AlertCircle className="h-5 w-5 shrink-0 text-rose-600 mt-0.5" />
              <div className="flex-1">
                <p className="font-bold text-rose-900">Gagal Masuk</p>
                <p className="mt-0.5 text-xs text-rose-700 leading-relaxed">{errorMessage}</p>
              </div>
            </div>
          )}

          {/* Main Card */}
          <div className="rounded-3xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-xl shadow-slate-900/5">
            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              {/* Email Field */}
              <div>
                <label
                  htmlFor="email"
                  className="block text-xs font-bold uppercase tracking-wider text-slate-700"
                >
                  Alamat Email
                </label>
                <div className="relative mt-1.5">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
                    <Mail className="h-4 w-4" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (formErrors.email) {
                        setFormErrors((prev) => ({ ...prev, email: undefined }));
                      }
                    }}
                    placeholder="nama@bilcode.id"
                    className={`w-full rounded-xl border bg-slate-50/60 py-3 pl-10 pr-3.5 text-sm text-slate-900 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-4 transition-all ${
                      formErrors.email
                        ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-100'
                        : 'border-slate-200 focus:border-emerald-600 focus:ring-emerald-500/10'
                    }`}
                  />
                </div>
                {formErrors.email && (
                  <p className="mt-1 text-xs text-rose-600 font-medium">{formErrors.email}</p>
                )}
              </div>

              {/* Password Field */}
              <div>
                <label
                  htmlFor="password"
                  className="block text-xs font-bold uppercase tracking-wider text-slate-700"
                >
                  Kata Sandi
                </label>
                <div className="relative mt-1.5">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
                    <Lock className="h-4 w-4" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (formErrors.password) {
                        setFormErrors((prev) => ({ ...prev, password: undefined }));
                      }
                    }}
                    placeholder="••••••••"
                    className={`w-full rounded-xl border bg-slate-50/60 py-3 pl-10 pr-11 text-sm text-slate-900 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-4 transition-all ${
                      formErrors.password
                        ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-100'
                        : 'border-slate-200 focus:border-emerald-600 focus:ring-emerald-500/10'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600 transition-colors"
                    aria-label={showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {formErrors.password && (
                  <p className="mt-1 text-xs text-rose-600 font-medium">{formErrors.password}</p>
                )}
              </div>

              {/* Submit Button with Luxury Gradient */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="group relative flex w-full items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-emerald-600 via-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 py-3.5 px-4 text-sm font-bold text-white shadow-lg shadow-emerald-600/25 transition-all duration-200 hover:scale-[1.01] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Memverifikasi Akun...</span>
                    </>
                  ) : (
                    <>
                      <span>Masuk ke Dashboard</span>
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Quick Presets for Evaluator */}
            <div className="mt-8 border-t border-slate-100 pt-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Pintasan Pengujian Cepat
                </span>
                <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200/60 px-2 py-0.5 rounded-xl">
                  1-Klik Auto-Fill
                </span>
              </div>

              <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                {/* Admin Quick Preset */}
                <button
                  type="button"
                  onClick={() => handleQuickPreset('admin', 'admin@bilcode.id', 'Admin123!')}
                  className={`flex flex-col text-left p-3 rounded-2xl border transition-all duration-200 ${
                    activePreset === 'admin'
                      ? 'border-emerald-500 bg-emerald-50/90 ring-2 ring-emerald-500/20 shadow-xs'
                      : 'border-slate-200/80 bg-slate-50/70 hover:bg-slate-100/80 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <div className="flex items-center gap-1.5 font-bold text-xs text-slate-900">
                      <ShieldCheck className="h-4 w-4 text-emerald-600 shrink-0" />
                      <span>Administrator</span>
                    </div>
                    <span className="text-[9px] font-extrabold uppercase tracking-wide bg-emerald-600 text-white px-1.5 py-0.5 rounded">
                      Admin
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-600">admin@bilcode.id</span>
                  <span className="text-[10px] text-emerald-700 font-semibold mt-1">
                    Hak Triage &amp; Status Full
                  </span>
                </button>

                {/* Citizen Quick Preset */}
                <button
                  type="button"
                  onClick={() => handleQuickPreset('user', 'user@bilcode.id', 'User123!')}
                  className={`flex flex-col text-left p-3 rounded-2xl border transition-all duration-200 ${
                    activePreset === 'user'
                      ? 'border-teal-500 bg-teal-50/90 ring-2 ring-teal-500/20 shadow-xs'
                      : 'border-slate-200/80 bg-slate-50/70 hover:bg-slate-100/80 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <div className="flex items-center gap-1.5 font-bold text-xs text-slate-900">
                      <UserCheck className="h-4 w-4 text-teal-600 shrink-0" />
                      <span>Warga Pelapor</span>
                    </div>
                    <span className="text-[9px] font-extrabold uppercase tracking-wide bg-teal-600 text-white px-1.5 py-0.5 rounded">
                      User
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-600">user@bilcode.id</span>
                  <span className="text-[10px] text-teal-700 font-semibold mt-1">
                    Lapor &amp; Riwayat Pribadi
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <AuthProvider>
      <LoginForm />
    </AuthProvider>
  );
}
