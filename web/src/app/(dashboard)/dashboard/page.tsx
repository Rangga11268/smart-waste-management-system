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
import { formatDate, cn } from '@/lib/utils';
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
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-heading text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Ringkasan Operasional
            </h1>
            {activeUsers !== null && (
              <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
                <Users className="h-3 w-3" />
                {activeUsers} Pengguna Aktif
              </span>
            )}
          </div>
          <p className="mt-1 font-sans text-sm text-slate-500">
            Pemantauan real-time metrik laporan sampah perkotaan dan aktivitas sistem terintegrasi.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <Link
            href="/reports"
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-xs hover:bg-slate-50 hover:text-slate-900 transition-all"
          >
            <span>Lihat Semua Laporan</span>
            <ArrowRight className="h-4 w-4 text-slate-400" />
          </Link>
          <button
            type="button"
            onClick={() => fetchStats(true)}
            disabled={isRefreshing || isLoading}
            className="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-primary-700 disabled:opacity-50 transition-all"
            aria-label="Segarkan data statistik"
          >
            <RotateCw
              className={cn('h-4 w-4 transition-transform', isRefreshing && 'animate-spin')}
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
              <h3 className="font-heading text-sm font-bold text-rose-900">
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
          {/* Card 1: Total Reports */}
          <StatCard
            title="Total Laporan Masuk"
            value={totalReports}
            subtitle={`${completedCount} laporan telah selesai`}
            icon={FileText}
            variant="default"
            isLoading={isLoading}
          />

          {/* Card 2: Pending Verification */}
          <StatCard
            title="Perlu Validasi"
            value={pendingCount}
            subtitle="Menunggu tinjauan awal petugas"
            icon={Clock}
            variant="amber"
            isLoading={isLoading}
          />

          {/* Card 3: In Progress */}
          <StatCard
            title="Sedang Ditangani"
            value={inProgressCount}
            subtitle="Armada kebersihan di lapangan"
            icon={Truck}
            variant="blue"
            isLoading={isLoading}
          />

          {/* Card 4: Completion Rate */}
          <StatCard
            title="Tingkat Penyelesaian"
            value={completionRateString}
            subtitle={
              rejectedCount > 0 ? `${rejectedCount} laporan ditolak` : 'Performa operasional tinggi'
            }
            icon={CheckCircle2}
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

      {/* Recent Activity Audit Stream Section */}
      <section
        aria-labelledby="recent-activity-heading"
        className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-200">
              <History className="h-4 w-4" />
            </div>
            <div>
              <h3 id="recent-activity-heading" className="font-heading text-lg font-bold text-slate-900">
                Aktivitas Terbaru
              </h3>
              <p className="font-sans text-xs text-slate-500">
                Log audit pergantian status laporan dan tindakan operasional terkini
              </p>
            </div>
          </div>
          <Link
            href="/reports"
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 inline-flex items-center gap-1 transition-colors self-start sm:self-auto"
          >
            <span>Buka Riwayat Lengkap</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {/* Activity Stream Feed */}
        <div className="mt-4">
          {isLoading ? (
            <div className="space-y-3 animate-pulse" data-testid="recent-activity-skeleton">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center justify-between p-3">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-slate-200" />
                    <div className="space-y-1.5">
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
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between py-3.5 px-3 rounded-lg hover:bg-slate-50/70 transition-colors gap-2"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-200 mt-0.5">
                      <Activity className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-sans text-sm font-medium text-slate-900">
                        {act.action}
                      </p>
                      <div className="mt-0.5 flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs text-slate-500">
                          ID: #{act.report_id}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="font-sans text-xs text-slate-400 pl-11 sm:pl-0 sm:text-right shrink-0">
                    {formatDate(act.timestamp)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-50 border border-slate-200 text-slate-400 mb-3">
                <Inbox className="h-6 w-6" />
              </div>
              <p className="font-heading text-sm font-semibold text-slate-700">
                Belum Ada Aktivitas Terbaru
              </p>
              <p className="mt-1 font-sans text-xs text-slate-400 max-w-sm">
                Log audit dan pembaruan status laporan sampah yang diproses oleh petugas akan tampil di sini.
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
