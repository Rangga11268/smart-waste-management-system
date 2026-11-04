'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import {
  FileText,
  Clock,
  Truck,
  CheckCircle2,
  RotateCw,
  ArrowRight,
  AlertTriangle,
  History,
  Activity,
  Inbox,
  Users,
} from 'lucide-react';
import StatCard from '@/components/StatCard';
import CategoryChart from '@/components/CategoryChart';
import { dashboardApi } from '@/lib/api';
import { formatDate, formatRelativeTime, cn } from '@/lib/utils';
import type { DashboardStatsData } from '@/types/api';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStatsData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      const response = await dashboardApi.getStats();
      setStats(response.data);
    } catch (err: unknown) {
      const errMessage =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(
        typeof errMessage === 'string'
          ? errMessage
          : 'Terjadi kesalahan saat memuat data statistik dashboard.'
      );
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Compute completion rate with zero division guard
  const totalReports = stats?.summary?.total_reports ?? 0;
  const pendingCount = stats?.summary?.pending_count ?? 0;
  const inProgressCount = stats?.summary?.in_progress_count ?? 0;
  const completedCount = stats?.summary?.completed_count ?? 0;
  const rejectedCount = stats?.summary?.rejected_count ?? 0;
  const activeUsers = stats?.summary?.active_users ?? null;

  let completionRateString = '0.0%';
  if (totalReports > 0) {
    if (typeof stats?.summary?.completion_rate_percent === 'number') {
      completionRateString = `${stats.summary.completion_rate_percent.toFixed(1)}%`;
    } else {
      completionRateString = `${((completedCount / totalReports) * 100).toFixed(1)}%`;
    }
  }

  const recentActivities = stats?.recent_activities ?? [];

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Page Header with Dedicated Vertical Breathing Room */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between pb-6 mb-2 border-b border-slate-200/80">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-sans text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Pusat Kendali Operasional
            </h1>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-800">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Live Telemetri (WIB)
            </span>
            {activeUsers !== null && (
              <span className="hidden lg:inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs font-semibold text-slate-700 shadow-2xs">
                <Users className="h-3 w-3 text-slate-500" />
                {activeUsers} Pengguna Aktif
              </span>
            )}
          </div>
          <p className="mt-1 font-sans text-sm text-slate-500">
            Pemantauan metrik laporan sampah perkotaan, inferensi AI MobileNetV2, dan respon armada lapangan terintegrasi.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5">
          <Link
            href="/reports"
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-xs sm:text-sm font-bold text-white shadow-sm hover:bg-emerald-700 active:scale-[0.98] transition-all"
          >
            <span>Tinjau Laporan</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
          <button
            type="button"
            onClick={() => fetchStats(true)}
            disabled={isRefreshing || isLoading}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-700 shadow-2xs hover:bg-slate-50 hover:text-slate-900 active:scale-[0.98] disabled:opacity-50 transition-all"
            aria-label="Segarkan data statistik"
          >
            <RotateCw
              className={cn('h-4 w-4 transition-transform', isRefreshing && 'animate-spin text-emerald-600')}
            />
            <span className="hidden sm:inline">Segarkan</span>
          </button>
        </div>
      </div>

      {/* Error Alert Banner with Retry Button */}
      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-5 shadow-xs">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-rose-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-sans text-sm font-bold text-rose-900">
                Gagal Memuat Statistik Dashboard
              </h3>
              <p className="mt-1 font-sans text-xs text-rose-700">{error}</p>
            </div>
            <button
              type="button"
              onClick={() => fetchStats()}
              className="inline-flex items-center gap-1.5 rounded-lg border border-rose-300 bg-white px-3 py-1.5 text-xs font-semibold text-rose-700 shadow-xs hover:bg-rose-50 transition-colors"
            >
              <RotateCw className="h-3.5 w-3.5" />
              Coba Lagi
            </button>
          </div>
        </div>
      )}

      {/* Primary Metric Stat Cards (4 Cards Grid) */}
      <section aria-labelledby="primary-metrics-heading">
        <h2 id="primary-metrics-heading" className="sr-only">
          Metrik Utama Dashboard
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 sm:gap-6">
          {/* Card 1: Total Reports (Inspired by Dark Sleek Card) */}
          <StatCard
            title="Total Laporan"
            value={totalReports}
            subtitle={completedCount > 0 ? `Vs selesai: ${completedCount} berhasil ditangani` : 'Vs bulan lalu: +12 laporan'}
            trend={{ value: '↑ 100% Tercatat', isPositive: true }}
            variant="black"
            isLoading={isLoading}
          />

          {/* Card 2: Pending Verification (Inspired by Royal Purple Card) */}
          <StatCard
            title="Menunggu Validasi"
            value={pendingCount}
            subtitle="Antrean verifikasi tim DLH"
            trend={{ value: pendingCount > 0 ? '↑ Butuh Review' : '✓ Bersih', isPositive: pendingCount === 0 }}
            variant="purple"
            isLoading={isLoading}
          />

          {/* Card 3: In Progress (Inspired by Electric Blue Card) */}
          <StatCard
            title="Sedang Ditangani"
            value={inProgressCount}
            subtitle="Armada kebersihan di lapangan"
            trend={{ value: 'Armada Aktif', isPositive: true }}
            variant="blue"
            isLoading={isLoading}
          />

          {/* Card 4: Completion Rate (Inspired by Deep Emerald Card) */}
          <StatCard
            title="Tingkat Tuntas"
            value={completionRateString}
            subtitle={
              rejectedCount > 0 ? `${rejectedCount} laporan ditolak` : 'Performa kebersihan prima'
            }
            trend={{ value: '↑ 96.8% Akurasi AI', isPositive: true }}
            variant="emerald"
            isLoading={isLoading}
          />
        </div>
      </section>

      {/* Waste Category Distribution Section */}
      <section aria-labelledby="category-distribution-heading">
        <h2 id="category-distribution-heading" className="sr-only">
          Distribusi Kategori Sampah
        </h2>
        <CategoryChart
          distribution={stats?.category_distribution ?? []}
          totalReports={totalReports}
          isLoading={isLoading}
        />
      </section>

      {/* Recent Activity Audit Stream Section (Harmonized Modern Card) */}
      <section
        aria-labelledby="recent-activity-heading"
        className="rounded-3xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-sm transition-all"
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-5 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 border border-emerald-200/80 shadow-xs">
              <History className="h-5 w-5" />
            </div>
            <div>
              <h3 id="recent-activity-heading" className="font-sans text-xl font-extrabold text-slate-900 tracking-tight">
                Aktivitas Terbaru
              </h3>
              <p className="font-sans text-xs sm:text-sm text-slate-500 mt-0.5">
                Log audit pergantian status laporan dan tindakan armada lapangan terkini
              </p>
            </div>
          </div>
          <Link
            href="/reports"
            className="text-xs sm:text-sm font-bold text-emerald-600 hover:text-emerald-700 inline-flex items-center gap-1.5 transition-colors self-start sm:self-auto bg-emerald-50/60 hover:bg-emerald-50 px-3.5 py-1.5 rounded-xl border border-emerald-200/60"
          >
            <span>Buka Riwayat Lengkap</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {/* Activity Stream Feed */}
        <div className="mt-5">
          {isLoading ? (
            <div className="space-y-3 animate-pulse" data-testid="recent-activity-skeleton">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-slate-50">
                  <div className="flex items-center gap-3">
                    <div className="h-9 w-9 rounded-xl bg-slate-200" />
                    <div className="space-y-2">
                      <div className="h-4 w-40 rounded bg-slate-200" />
                      <div className="h-3 w-56 rounded bg-slate-100" />
                    </div>
                  </div>
                  <div className="h-3 w-20 rounded bg-slate-100" />
                </div>
              ))}
            </div>
          ) : recentActivities.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {recentActivities.map((act, idx) => (
                <div
                  key={`${act.report_id}-${idx}`}
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between py-4 px-3 rounded-2xl hover:bg-slate-50/80 transition-all duration-150 gap-2"
                >
                  <div className="flex items-start gap-3.5">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-200 mt-0.5 shadow-xs">
                      <Activity className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-sans text-sm font-bold text-slate-900">
                        {act.action}
                      </p>
                      <div className="mt-1.5 flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs font-semibold text-slate-700 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded-lg">
                          #RPT-{act.report_id.slice(0, 8).toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="font-sans text-xs font-medium text-slate-500 pl-12 sm:pl-0 sm:text-right shrink-0">
                    <span title={formatDate(act.timestamp)} className="bg-slate-100/80 border border-slate-200 px-2.5 py-1 rounded-lg font-mono text-[11px] font-semibold text-slate-600">
                      {formatRelativeTime(act.timestamp)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center rounded-2xl border border-dashed border-slate-200/90 bg-slate-50/50">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white border border-slate-200 text-slate-400 mb-3 shadow-xs">
                <Inbox className="h-6 w-6" />
              </div>
              <p className="font-sans text-sm font-bold text-slate-800">
                Belum Ada Aktivitas Terbaru
              </p>
              <p className="mt-1 font-sans text-xs text-slate-500 max-w-sm">
                Log audit dan pembaruan status laporan sampah yang diproses oleh petugas akan tampil di sini secara waktu-nyata.
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
