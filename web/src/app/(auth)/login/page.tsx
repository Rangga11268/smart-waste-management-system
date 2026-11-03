'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
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
  Sparkles,
  MapPin,
  CheckCircle2,
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

  const handleQuickPreset = (presetEmail: string, presetPass: string) => {
    setEmail(presetEmail);
    setPassword(presetPass);
    setFormErrors({});
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col lg:grid lg:grid-cols-12">
      {/* Left Brand Showcase Column (Desktop Only) */}
      <div className="hidden lg:col-span-5 lg:flex lg:flex-col lg:justify-between bg-slate-900 p-12 text-white relative overflow-hidden border-r border-slate-800">
        <div className="relative z-10">
          <Logo size={42} showText={true} />
          
          <div className="mt-12 space-y-5">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Sistem Pengelolaan Sampah Cerdas Terintegrasi
            </div>
            
            <h1 className="text-3xl font-extrabold tracking-tight text-white leading-tight font-sans">
              Akselerasi Keberlanjutan Kota dengan Computer Vision & Geotagging.
            </h1>
            
            <p className="text-sm text-slate-300 leading-relaxed font-sans">
              SWMS menghubungkan pelaporan warga, inferensi AI MobileNetV2 presisi tinggi, dan dashboard armada kebersihan dalam satu ekosistem waktu-nyata.
            </p>
          </div>

          <div className="mt-10 space-y-4 font-sans text-xs">
            <div className="flex items-center gap-3 text-slate-200">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <Sparkles className="h-4 w-4" />
              </div>
              <span>Klasifikasi Citra Sampah Otomatis (Organik, Plastik, Kertas)</span>
            </div>
            <div className="flex items-center gap-3 text-slate-200">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <MapPin className="h-4 w-4" />
              </div>
              <span>Geocoding Terbalik Otomatis & Alamat Lapangan Presisi</span>
            </div>
            <div className="flex items-center gap-3 text-slate-200">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <CheckCircle2 className="h-4 w-4" />
              </div>
              <span>Audit Trail Disposisi Status Lengkap Tanpa Kehilangan Data</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 border-t border-slate-800 pt-6 mt-12 flex items-center justify-between text-xs text-slate-400">
          <span>&copy; 2026 PT Bilcode Teknologi Indonesia</span>
          <span className="font-mono text-emerald-400">v1.0.0 Production</span>
        </div>
      </div>

      {/* Right Login Form Column */}
      <div className="flex-1 lg:col-span-7 flex flex-col justify-center px-4 py-12 sm:px-6 lg:px-12 xl:px-16">
        <div className="mx-auto w-full max-w-md">
          {/* Mobile Logo Brand */}
          <div className="lg:hidden flex items-center justify-center mb-8">
            <Logo size={48} showText={true} />
          </div>

          <div className="mb-8">
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 font-heading">
              Selamat Datang
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Masukkan kredensial akun Anda untuk mengakses portal manajemen SWMS.
            </p>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div
              className="mb-6 flex items-start gap-3 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 shadow-xs"
              role="alert"
            >
              <AlertCircle className="h-5 w-5 shrink-0 text-rose-600 mt-0.5" />
              <div className="flex-1">
                <p className="font-bold text-rose-900">Gagal Masuk</p>
                <p className="mt-0.5 text-xs text-rose-700 leading-relaxed">{errorMessage}</p>
              </div>
            </div>
          )}

          <div className="rounded-2xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-[0_2px_12px_-4px_rgba(15,23,42,0.06)]">
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
                    className={`w-full rounded-xl border bg-slate-50/50 py-2.5 pl-10 pr-3.5 text-sm text-slate-900 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 transition-all ${
                      formErrors.email
                        ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-200'
                        : 'border-slate-200 focus:border-emerald-600 focus:ring-emerald-600/20'
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
                    className={`w-full rounded-xl border bg-slate-50/50 py-2.5 pl-10 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 transition-all ${
                      formErrors.password
                        ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-200'
                        : 'border-slate-200 focus:border-emerald-600 focus:ring-emerald-600/20'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600"
                    aria-label={showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {formErrors.password && (
                  <p className="mt-1 text-xs text-rose-600 font-medium">{formErrors.password}</p>
                )}
              </div>

              {/* Submit Button */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="group flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white shadow-sm hover:bg-emerald-700 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60 transition-all"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Memverifikasi Akun...</span>
                    </>
                  ) : (
                    <>
                      <span>Masuk ke Dashboard</span>
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Quick Presets for Evaluator */}
            <div className="mt-6 border-t border-slate-100 pt-5">
              <p className="text-center text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Pintasan Pengujian Cepat
              </p>
              <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
                <button
                  type="button"
                  onClick={() => handleQuickPreset('admin@bilcode.id', 'Admin123!')}
                  className="flex items-center justify-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50/80 px-3 py-2 text-xs font-bold text-emerald-800 hover:bg-emerald-100 transition-all shadow-2xs"
                >
                  <ShieldCheck className="h-4 w-4 text-emerald-600 shrink-0" />
                  <span>Login Administrator</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickPreset('user@bilcode.id', 'User123!')}
                  className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-slate-100 transition-all shadow-2xs"
                >
                  <UserCheck className="h-4 w-4 text-slate-500 shrink-0" />
                  <span>Login Warga Pelapor</span>
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
