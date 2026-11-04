'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  Sparkles,
  Play,
  Menu,
  X,
  ExternalLink,
  Cpu,
  Server,
  Smartphone,
  Database,
  Layers,
} from 'lucide-react';
import Logo from '@/components/Logo';

export interface ResponsiveHeroBannerProps {
  badgeLabel?: string;
  badgeText?: string;
  title?: string;
  titleLine2?: string;
  description?: string;
  primaryButtonText?: string;
  primaryButtonHref?: string;
  secondaryButtonText?: string;
  secondaryButtonHref?: string;
  isAuthenticated?: boolean;
}

export default function ResponsiveHeroBanner({
  badgeLabel = 'BARU v1.0',
  badgeText = 'AI MobileNetV2 Vision & GPS Geotagging 2026',
  title = 'Akselerasi Keberlanjutan Kota',
  titleLine2 = 'dengan AI Vision & Geotagging',
  description = 'SWMS menghubungkan pelaporan foto bukti warga, inferensi model AI MobileNetV2 berkecepatan tinggi, serta orkestrasi armada kebersihan lapangan secara waktu-nyata tanpa kehilangan data.',
  primaryButtonText = 'Akses Dashboard Operasional',
  primaryButtonHref = '/dashboard',
  secondaryButtonText = 'Tinjau Laporan Sampah',
  secondaryButtonHref = '/reports',
  isAuthenticated = false,
}: ResponsiveHeroBannerProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { label: 'Beranda', href: '#', isActive: true },
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Laporan', href: '/reports' },
    { label: 'Dokumentasi', href: 'http://localhost:8000/docs', isExternal: true },
  ];

  const techPartners = [
    { name: 'PyTorch MobileNetV2', icon: Cpu, label: 'Model AI' },
    { name: 'FastAPI Python 3.12', icon: Server, label: 'REST Core' },
    { name: 'Next.js 14 App Router', icon: Layers, label: 'Web Console' },
    { name: 'Flutter Android APK', icon: Smartphone, label: 'Mobile App' },
    { name: 'PostgreSQL & SQLite', icon: Database, label: 'Audit Trail' },
  ];

  return (
    <section className="w-full isolate min-h-screen overflow-hidden relative flex flex-col justify-between bg-slate-950 font-sans selection:bg-emerald-600 selection:text-white">
      {/* Cinematic AI-Generated Eco-Tech Smart City Background Image */}
      <img
        src="/hero-bg.jpg"
        alt="SWMS Eco-Tech Smart City"
        className="w-full h-full object-cover absolute inset-0 opacity-40 scale-105 pointer-events-none transition-transform duration-1000 ease-out"
      />
      
      {/* Multi-Stage Dark Slate & Ambient Vignette */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-slate-950/90 via-slate-950/75 to-slate-950" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_20%,rgba(2,6,23,0.85)_100%)]" />

      {/* Luxury Ambient Glow Orbs */}
      <div className="pointer-events-none absolute top-1/4 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[350px] bg-emerald-500/15 blur-[140px] rounded-full" />
      <div className="pointer-events-none absolute top-1/3 right-1/4 translate-x-1/3 -translate-y-1/2 w-[550px] h-[300px] bg-teal-500/10 blur-[150px] rounded-full" />

      {/* Floating Glassmorphic Header Navigation */}
      <header className="z-20 w-full pt-4 sm:pt-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Brand Logo */}
          <Link href="/" className="inline-flex items-center group">
            <Logo size={36} showText={true} variant="inverted" />
          </Link>

          {/* Desktop Center Floating Glass Pill Nav */}
          <nav className="hidden md:flex items-center gap-2">
            <div className="flex items-center gap-1 rounded-2xl bg-slate-900/70 px-2 py-1.5 border border-white/10 backdrop-blur-xl shadow-2xl shadow-black/50">
              {navLinks.map((link, idx) => (
                link.isExternal ? (
                  <a
                    key={idx}
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition-colors inline-flex items-center gap-1"
                  >
                    <span>{link.label}</span>
                    <ExternalLink className="h-3 w-3 text-emerald-400" />
                  </a>
                ) : (
                  <Link
                    key={idx}
                    href={link.href}
                    className={`px-3.5 py-1.5 text-xs font-semibold transition-colors rounded-xl ${
                      link.isActive
                        ? 'text-white bg-white/10 shadow-xs'
                        : 'text-slate-300 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {link.label}
                  </Link>
                )
              ))}

              {/* Action Button inside Pill */}
              <Link
                href={isAuthenticated ? '/dashboard' : '/login'}
                className="ml-1 inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-emerald-500 via-emerald-600 to-teal-500 px-4 py-1.5 text-xs font-bold text-white shadow-lg shadow-emerald-600/30 hover:shadow-emerald-500/50 hover:from-emerald-400 hover:to-teal-400 transition-all border border-emerald-400/30"
              >
                <span>{isAuthenticated ? 'Dashboard' : 'Masuk Portal'}</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </nav>

          {/* Mobile Hamburger Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900/80 border border-white/15 backdrop-blur-md text-white shadow-lg"
            aria-expanded={mobileMenuOpen}
            aria-label="Buka menu navigasi"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-3 rounded-2xl border border-slate-800 bg-slate-900/95 p-4 backdrop-blur-xl shadow-2xl space-y-2">
            {navLinks.map((link, idx) => (
              <Link
                key={idx}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-xl text-sm font-semibold text-slate-200 hover:bg-slate-800 hover:text-white"
              >
                {link.label}
              </Link>
            ))}
            <div className="pt-2 border-t border-slate-800">
              <Link
                href={isAuthenticated ? '/dashboard' : '/login'}
                onClick={() => setMobileMenuOpen(false)}
                className="block text-center rounded-xl bg-gradient-to-r from-emerald-500 via-emerald-600 to-teal-600 px-4 py-2.5 text-sm font-bold text-white shadow-lg shadow-emerald-600/30"
              >
                {isAuthenticated ? 'Buka Dashboard' : 'Masuk Portal'}
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* Main Hero Content */}
      <div className="z-10 relative my-auto py-12 sm:py-16 lg:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          {/* Clean Eyebrow Category Title (No Capsule, No Blinking Dot) */}
          <div className="mb-6 flex items-center justify-center gap-2.5 text-xs sm:text-sm font-bold tracking-wide animate-fade-slide-in-1">
            <span className="text-emerald-400 uppercase tracking-widest">{badgeLabel}</span>
            <span className="text-slate-600 font-normal">/</span>
            <span className="text-slate-300 font-medium">{badgeText}</span>
          </div>

          {/* Headline (Inter Sans-Serif font, Bold, Crisp, Luxury Gradient) */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-white tracking-tight leading-[1.1] animate-fade-slide-in-2 font-sans">
            {title}
            <br className="hidden sm:block" />{' '}
            <span className="block mt-2 sm:mt-1 bg-gradient-to-r from-emerald-300 via-teal-200 to-emerald-400 bg-clip-text text-transparent font-black drop-shadow-[0_2px_25px_rgba(16,185,129,0.35)]">
              {titleLine2}
            </span>
          </h1>

          {/* Description Subtitle */}
          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mt-6 mx-auto leading-relaxed font-normal animate-fade-slide-in-3">
            {description}
          </p>

          {/* Dual Action CTA Buttons */}
          <div className="flex flex-col sm:flex-row sm:gap-4 mt-8 sm:mt-10 gap-3 items-center justify-center animate-fade-slide-in-4">
            <Link
              href={primaryButtonHref}
              className="group relative w-full sm:w-auto inline-flex items-center justify-center gap-2.5 overflow-hidden rounded-xl bg-gradient-to-r from-emerald-500 via-emerald-600 to-teal-600 px-8 py-4 text-sm font-bold text-white shadow-[0_0_35px_-5px_rgba(16,185,129,0.5)] hover:shadow-[0_0_50px_0_rgba(16,185,129,0.7)] border border-emerald-400/40 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
            >
              <span>{primaryButtonText}</span>
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1 text-emerald-100" />
            </Link>

            <Link
              href={secondaryButtonHref}
              className="group w-full sm:w-auto inline-flex items-center justify-center gap-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800/80 border border-slate-700/80 hover:border-emerald-500/50 px-7 py-4 text-sm font-semibold text-slate-200 hover:text-white backdrop-blur-xl shadow-xl shadow-black/40 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
            >
              <Play className="h-3.5 w-3.5 fill-current text-emerald-400 group-hover:text-emerald-300 transition-colors" />
              <span>{secondaryButtonText}</span>
            </Link>
          </div>
        </div>

        {/* Tech Ecosystem & Standard Grid (Luxury Micro-Cards) */}
        <div className="mx-auto mt-16 sm:mt-20 max-w-5xl">
          <p className="text-xs uppercase tracking-widest text-slate-400 text-center font-bold animate-fade-slide-in-1">
            Didukung Ekosistem Arsitektur Fullstack &amp; Standar Bilcode Technology
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 text-slate-300 mt-6 items-center justify-items-center gap-3 animate-fade-slide-in-2">
            {techPartners.map((tech, idx) => {
              const Icon = tech.icon;
              return (
                <div
                  key={idx}
                  className="w-full flex items-center justify-center gap-2.5 py-3 px-3.5 rounded-2xl bg-slate-900/60 hover:bg-slate-800/70 border border-slate-800/90 hover:border-emerald-500/40 backdrop-blur-md text-xs font-semibold text-slate-300 hover:text-white transition-all duration-300 shadow-sm hover:shadow-[0_0_20px_-5px_rgba(16,185,129,0.25)] group"
                >
                  <Icon className="h-4 w-4 text-emerald-400 group-hover:text-emerald-300 transition-colors shrink-0" />
                  <span className="truncate">{tech.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Bottom Subtle Gradient Transition to Next Section */}
      <div className="h-16 bg-gradient-to-b from-transparent to-slate-50 relative z-10 pointer-events-none" />
    </section>
  );
}
