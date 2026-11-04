"use client";

import { Card } from "@/components/ui/card";
import React from "react";
import Link from "next/link";
import { ArrowRight, Info, ShieldCheck, Zap, Activity } from "lucide-react";

export function AboutBento() {
  return (
    <section className="bg-slate-50 py-16 px-4 sm:py-24 sm:px-6 font-sans border-t border-slate-200">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12 sm:mb-16">
          <p className="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-2">
            Dampak Nyata Lapangan
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight mb-4">
            About Our Environmental Impact
          </h2>
          <p className="text-base sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed font-normal">
            Menghubungkan partisipasi ribuan warga, otomasi klasifikasi MobileNetV2, dan respons cepat armada kebersihan kota menuju target Zero-Waste.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-5 sm:gap-6">
          {/* Card 1: Large Feature (Clean Slate with Subtle Geometry) */}
          <Card className="md:col-span-2 md:row-span-2 bg-white rounded-3xl p-6 sm:p-10 lg:p-12 flex flex-col justify-between border border-slate-200/90 relative overflow-hidden group shadow-sm hover:shadow-xl transition-all duration-300">
            <svg
              width="377"
              height="368"
              className="w-[280px] sm:w-[380px] fill-slate-100/80 absolute -bottom-16 group-hover:rotate-180 transition-transform duration-1000 ease-in-out -right-16 pointer-events-none"
              viewBox="0 0 377 368"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path d="M179.692 5.79814C182.635 -1.93287 193.572 -1.93285 196.515 5.79816L229.505 92.466C231.206 96.9342 236.103 99.2928 240.657 97.8366L328.986 69.5929C336.865 67.0735 343.684 75.6242 339.474 82.7452L292.284 162.574C289.851 166.69 291.061 171.99 295.038 174.642L372.192 226.091C379.075 230.68 376.641 241.343 368.449 242.491L276.613 255.369C271.878 256.033 268.489 260.283 268.895 265.047L276.776 357.445C277.479 365.688 267.625 370.433 261.619 364.744L194.293 300.973C190.821 297.686 185.386 297.686 181.914 300.973L114.588 364.744C108.582 370.433 98.7281 365.688 99.4311 357.445L107.312 265.047C107.718 260.283 104.329 256.033 99.5941 255.369L7.7582 242.491C-0.433812 241.343 -2.86746 230.68 4.01488 226.091L81.1687 174.642C85.1465 171.99 86.3561 166.69 83.9231 162.574L36.7325 82.7452C32.523 75.6242 39.342 67.0735 47.2212 69.5929L135.55 97.8366C140.104 99.2928 145.001 96.9342 146.702 92.4659L179.692 5.79814Z" />
            </svg>
            <div className="space-y-4 sm:space-y-6 relative z-10">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 block">
                Citywide Reach
              </span>
              <h3 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tighter leading-tight">
                IMPACT WITHOUT
                <br />
                BOUNDARIES.
              </h3>
              <p className="text-base sm:text-lg text-slate-600 font-normal leading-relaxed max-w-sm">
                Mengkoordinasikan pelaporan timbulan sampah warga dengan akurasi disposisi audit 100%.
              </p>
            </div>

            {/* Zero-Void Structured 3-Metric Summary */}
            <div className="mt-8 pt-6 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-2.5 relative z-10">
              <div className="bg-slate-50 rounded-2xl p-3.5 border border-slate-200/80">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">Audit Log</span>
                <span className="text-sm font-black text-slate-900 mt-1 block">100% Tercatat</span>
              </div>
              <div className="bg-slate-50 rounded-2xl p-3.5 border border-slate-200/80">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">Waktu Respon</span>
                <span className="text-sm font-black text-emerald-700 mt-1 block">&lt;15 Menit</span>
              </div>
              <div className="bg-slate-50 rounded-2xl p-3.5 border border-slate-200/80">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">Geotagging</span>
                <span className="text-sm font-black text-slate-900 mt-1 block">GPS Presisi</span>
              </div>
            </div>
          </Card>

          {/* Card 2: Growth Metric (Deep Forest Emerald Card) */}
          <Card className="bg-gradient-to-br from-emerald-600 to-emerald-800 rounded-3xl p-6 sm:p-8 lg:p-10 text-white flex flex-col border-none justify-between shadow-lg shadow-emerald-700/20 hover:scale-[1.01] transition-transform">
            <span className="text-xs font-black uppercase tracking-widest text-emerald-100">
              Avg Speedup
            </span>
            <div className="space-y-2 mt-4 sm:mt-0">
              <span className="text-5xl sm:text-6xl font-black tracking-tighter">450%</span>
              <p className="text-xs sm:text-sm text-emerald-100 font-normal leading-snug">
                Peningkatan efisiensi waktu penanganan armada kebersihan kota
              </p>
              <div className="h-2 w-full bg-white/20 rounded-full overflow-hidden mt-3">
                <div className="h-full w-4/5 bg-white rounded-full shadow-[0_0_12px_rgba(255,255,255,0.9)]" />
              </div>
            </div>
          </Card>

          {/* Card 3: AI Engine (Dark Slate Card with Emerald Micro-badge) */}
          <Card className="bg-slate-900 rounded-3xl p-6 sm:p-8 lg:p-10 text-white flex flex-col justify-between gap-4 border border-slate-800 shadow-lg shadow-slate-950/20 hover:scale-[1.01] transition-transform">
            <div className="flex items-center justify-between">
              <div className="h-10 w-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 flex items-center justify-center shadow-xs">
                <Zap className="h-5 w-5 text-emerald-400" />
              </div>
              <span className="font-mono text-[11px] font-bold text-emerald-400 bg-emerald-950/70 border border-emerald-800/80 px-2.5 py-0.5 rounded-md">
                &lt;100ms Inference
              </span>
            </div>

            <div>
              <h4 className="text-xl font-bold tracking-tight text-white leading-tight">
                MobileNetV2 Edge
              </h4>
              <p className="text-xs text-slate-300 mt-1">
                Klasifikasi Otomatis Organik, Plastik, & Kertas
              </p>
            </div>

            {/* Awam-Friendly Explanation Box */}
            <div className="rounded-xl bg-slate-800/90 p-3 border border-slate-700/70 text-[11px] text-slate-300 leading-relaxed flex items-start gap-2">
              <Info className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong className="text-emerald-400">AI Ringan di Ponsel:</strong> Memproses foto sampah seketika tanpa membebani perangkat pelapor.
              </span>
            </div>
          </Card>

          {/* Card 4: Community Call to Action (Deep Navy/Slate Card with Emerald CTA) */}
          <Card className="md:col-span-2 rounded-3xl p-6 sm:p-8 border border-slate-800 flex flex-col sm:flex-row gap-5 items-start sm:items-center justify-between cursor-pointer bg-slate-900 text-white shadow-xl shadow-slate-950/30 hover:border-slate-700 transition-all duration-300 group overflow-hidden">
            <div className="space-y-2 relative z-10">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 block">
                Partisipasi Publik
              </span>
              <h4 className="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white">
                Bergabung dengan SWMS
              </h4>
              <p className="text-slate-300 text-sm max-w-md font-normal leading-relaxed">
                Jadilah pelapor aktif kebersihan lingkungan dan bantu koordinasi penjemputan sampah secara akurat.
              </p>
            </div>
            <Link
              href="/login"
              className="h-14 w-14 sm:h-16 sm:w-16 shrink-0 rounded-2xl flex items-center justify-center bg-emerald-600 text-white shadow-lg shadow-emerald-600/30 group-hover:scale-105 group-hover:bg-emerald-500 transition-all duration-300 relative z-10 min-h-[44px] min-w-[44px]"
              aria-label="Masuk ke portal SWMS"
            >
              <ArrowRight className="h-6 w-6 text-white" />
            </Link>
          </Card>
        </div>
      </div>
    </section>
  );
}

export default AboutBento;
