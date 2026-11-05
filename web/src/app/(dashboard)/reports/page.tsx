'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Search,
  Filter,
  RotateCcw,
  RotateCw,
  Eye,
  ChevronLeft,
  ChevronRight,
  Inbox,
  AlertCircle,
  Loader2,
  FileSpreadsheet,
  Plus,
  MapPin,
  ExternalLink,
} from 'lucide-react';
import StatusBadge from '@/components/StatusBadge';
import CategoryBadge from '@/components/CategoryBadge';
import ReportModal from '@/components/ReportModal';
import CreateReportModal from '@/components/CreateReportModal';
import { useAuth } from '@/lib/auth';
import { reportsApi, categoriesApi, getFullImageUrl } from '@/lib/api';
import { formatDate, formatRelativeTime, getGoogleMapsUrl, cn } from '@/lib/utils';
import type {
  ReportListItem,
  ReportDetailData,
  WasteCategory,
  ReportStatus,
} from '@/types/api';

export default function ReportsPage() {
  const { user } = useAuth();

  // Reports and pagination state
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [page, setPage] = useState<number>(1);
  const limit = 10;

  // Filter & Search states
  const [searchInput, setSearchInput] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [onlyMyReports, setOnlyMyReports] = useState<boolean>(false);

  // Categories list
  const [categories, setCategories] = useState<WasteCategory[]>([]);

  // Async loading & error states
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Review & Create modal states
  const [selectedReport, setSelectedReport] = useState<ReportListItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState<boolean>(false);

  // Fallback images map for failed image loads
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({});

  // 300ms Debounce for keyword search input
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchInput);
      setPage(1);
    }, 300);

    return () => clearTimeout(handler);
  }, [searchInput]);

  // Fetch categories catalog
  useEffect(() => {
    async function loadCategories() {
      try {
        const res = await categoriesApi.getCategories();
        setCategories(res.data);
      } catch {
        // Fallback static categories if catalog API is unavailable
        setCategories([
          { id: 1, name: 'Organic Waste', slug: 'organic', badge_color: '#16a34a' },
          { id: 2, name: 'Plastic Waste', slug: 'plastic', badge_color: '#0284c7' },
          { id: 3, name: 'Paper Waste', slug: 'paper', badge_color: '#d97706' },
        ]);
      }
    }
    loadCategories();
  }, []);

  // Fetch reports from API
  const fetchReports = useCallback(
    async (showLoadingSpinner = true) => {
      if (showLoadingSpinner) {
        setIsLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);

      try {
        const params: {
          page: number;
          limit: number;
          status?: string;
          category_id?: number;
          search?: string;
        } = {
          page,
          limit,
        };

        if (statusFilter) {
          params.status = statusFilter;
        }
        if (categoryFilter) {
          const parsedCat = parseInt(categoryFilter, 10);
          if (!isNaN(parsedCat)) {
            params.category_id = parsedCat;
          }
        }
        if (debouncedSearch.trim()) {
          params.search = debouncedSearch.trim();
        }

        const res = await reportsApi.getReports(params);
        setReports(res.data);
        setTotalItems(res.meta.total_items);
        setTotalPages(res.meta.total_pages || 1);
      } catch (err: unknown) {
        const msg =
          err && typeof err === 'object' && 'response' in err
            ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
            : null;
        setError(
          typeof msg === 'string'
            ? msg
            : 'Terjadi kesalahan saat mengambil daftar laporan sampah.'
        );
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    [page, limit, statusFilter, categoryFilter, debouncedSearch]
  );

  // Trigger report fetch when query dependencies change
  useEffect(() => {
    fetchReports(true);
  }, [fetchReports]);

  // Reset filters handler
  const handleResetFilters = () => {
    setSearchInput('');
    setDebouncedSearch('');
    setStatusFilter('');
    setCategoryFilter('');
    setPage(1);
  };

  // Open detail review modal
  const handleOpenReviewModal = (report: ReportListItem) => {
    setSelectedReport(report);
    setIsModalOpen(true);
  };

  // Close review modal
  const handleCloseReviewModal = () => {
    setIsModalOpen(false);
    setSelectedReport(null);
  };

  // Handle report status updated from modal
  const handleReportUpdated = (updatedReport: ReportDetailData) => {
    // 1. Immediately update local report in table list
    setReports((prevReports) =>
      prevReports.map((r) =>
        r.id === updatedReport.id
          ? {
              ...r,
              status: updatedReport.status,
              category: updatedReport.category || r.category,
            }
          : r
      )
    );

    // 2. Refresh silently to keep pagination counts and server state in perfect sync
    fetchReports(false);
  };

  const hasActiveFilters = useMemo(
    () => Boolean(searchInput || statusFilter || categoryFilter),
    [searchInput, statusFilter, categoryFilter]
  );

  // Client-side CSV Exporter (Zero-cost, instant municipal download)
  const handleExportCSV = () => {
    if (reports.length === 0) return;
    const headers = ['ID Laporan', 'Pelapor', 'Kategori', 'Akurasi AI', 'Status', 'Alamat / Catatan', 'Latitude', 'Longitude', 'Tanggal Lapor'];
    const rows = reports.map((r) => [
      `"${r.id}"`,
      `"${r.reporter?.full_name || r.reporter?.email || '-'}"`,
      `"${r.category?.name || '-'}"`,
      `"${r.ai_confidence ? (r.ai_confidence * 100).toFixed(1) + '%' : '-'}"`,
      `"${r.status}"`,
      `"${(r.address_note || r.title || '').replace(/"/g, '""')}"`,
      r.latitude,
      r.longitude,
      `"${new Date(r.created_at).toLocaleString('id-ID')}"`,
    ]);
    const csvContent = '\uFEFF' + [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `SWMS_Laporan_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const displayedReports = useMemo(() => {
    if (!onlyMyReports || !user) return reports;
    return reports.filter((r) => r.reporter?.id === user.id);
  }, [reports, onlyMyReports, user]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="font-sans text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Laporan Sampah Perkotaan
            </h1>
            <span className="rounded-md border border-slate-200 bg-white px-2 py-0.5 text-xs font-semibold text-slate-600 shadow-2xs">
              {totalItems} Total
            </span>
          </div>
          <p className="mt-1 font-sans text-sm text-slate-500">
            Kelola, filter, dan tinjau laporan sampah warga serta pantau status penanganan secara berkala.
          </p>
        </div>

        {/* Action Buttons - Reflowed for mobile with equal height and clear hierarchy */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 w-full sm:w-auto">
          <button
            type="button"
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-xs sm:text-sm font-bold text-white shadow-sm hover:bg-emerald-700 active:scale-[0.98] transition-all min-h-[44px] order-1 sm:order-2 text-center"
          >
            <Plus className="h-4 w-4" />
            <span>Buat Laporan Baru</span>
          </button>
          <div className="grid grid-cols-2 sm:flex sm:items-center gap-2 order-2 sm:order-1">
            <button
              type="button"
              onClick={handleExportCSV}
              disabled={reports.length === 0}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200/80 bg-white px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-700 shadow-2xs hover:bg-slate-50 hover:text-slate-900 active:scale-[0.98] transition-all disabled:opacity-50 min-h-[44px] text-center"
              title="Unduh seluruh data laporan saat ini ke format file CSV"
            >
              <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
              <span>Ekspor CSV</span>
            </button>
            <button
              type="button"
              onClick={() => fetchReports(false)}
              disabled={isRefreshing || isLoading}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200/80 bg-white px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-700 shadow-2xs hover:bg-slate-50 hover:text-slate-900 active:scale-[0.98] transition-all disabled:opacity-50 min-h-[44px] text-center"
            >
              <RotateCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin text-emerald-600' : ''}`} />
              <span>Segarkan</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="rounded-2xl border border-slate-200/90 bg-white p-4 sm:p-5 shadow-[0_1px_3px_rgba(15,23,42,0.04)] space-y-3.5">
        {/* Quick Status Filter Tabs - Smooth horizontal scroll on mobile with no awkward orphan chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none border-b border-slate-100 -mx-4 px-4 sm:mx-0 sm:px-0">
          {[
            { label: 'Semua Status', value: '' },
            { label: 'Menunggu Validasi', value: 'Pending' },
            { label: 'Sedang Ditangani', value: 'In Progress' },
            { label: 'Selesai Ditangani', value: 'Completed' },
            { label: 'Ditolak', value: 'Rejected' },
          ].map((tab) => {
            const isTabActive = statusFilter === tab.value;
            return (
              <button
                key={tab.value}
                type="button"
                onClick={() => {
                  setStatusFilter(tab.value);
                  setPage(1);
                }}
                className={cn(
                  'px-3.5 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap shrink-0 min-h-[38px] flex items-center justify-center',
                  isTabActive
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                )}
              >
                {tab.label}
              </button>
            );
          })}

          {user && (
            <div className="flex items-center gap-1.5 pl-2 sm:pl-3 border-l border-slate-200 shrink-0">
              <button
                type="button"
                onClick={() => setOnlyMyReports(!onlyMyReports)}
                className={cn(
                  'px-3.5 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap min-h-[38px] flex items-center justify-center',
                  onlyMyReports
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                )}
              >
                Laporan Saya
              </button>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
          {/* Keyword Search Input with 300ms debounce */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Cari judul, deskripsi, atau patokan lokasi..."
              className="w-full rounded-xl border border-slate-200 bg-slate-50/50 pl-10 pr-4 py-2.5 text-xs sm:text-sm text-slate-900 placeholder:text-slate-400 focus:bg-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all"
            />
          </div>

          {/* Filter Dropdowns Container */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Status Filter Dropdown (Hidden on mobile since status filter tabs above already handle this) */}
            <div className="hidden sm:flex items-center gap-1.5 min-w-[140px]">
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1);
                }}
                className="w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2.5 text-xs sm:text-sm text-slate-700 focus:bg-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all font-medium"
                aria-label="Filter berdasarkan status"
              >
                <option value="">Semua Status</option>
                <option value="Pending">Menunggu Validasi (Pending)</option>
                <option value="In Progress">Sedang Ditangani (In Progress)</option>
                <option value="Completed">Selesai Ditangani (Completed)</option>
                <option value="Rejected">Laporan Ditolak (Rejected)</option>
              </select>
            </div>

            {/* Category Filter */}
            <div className="flex-1 sm:flex-initial flex items-center gap-1.5 min-w-[140px]">
              <select
                value={categoryFilter}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setPage(1);
                }}
                className="w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2.5 text-xs sm:text-sm text-slate-700 focus:bg-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all font-medium"
                aria-label="Filter berdasarkan kategori sampah"
              >
                <option value="">Semua Kategori</option>
                {categories.length > 0 ? (
                  categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.id})
                    </option>
                  ))
                ) : (
                  <>
                    <option value="1">Organic Waste (1)</option>
                    <option value="2">Plastic Waste (2)</option>
                    <option value="3">Paper Waste (3)</option>
                  </>
                )}
              </select>
            </div>

            {/* Reset Filters Button */}
            {hasActiveFilters && (
              <button
                type="button"
                onClick={handleResetFilters}
                className="inline-flex items-center gap-1.5 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2.5 text-xs font-semibold text-rose-700 hover:bg-rose-100 transition-colors shadow-2xs"
                title="Bersihkan semua filter"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="flex items-center justify-between rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs sm:text-sm text-rose-800">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="h-5 w-5 shrink-0 text-rose-600" />
            <p className="font-medium">{error}</p>
          </div>
          <button
            type="button"
            onClick={() => fetchReports(true)}
            className="rounded-lg bg-rose-100 px-3 py-1 font-semibold text-rose-800 hover:bg-rose-200 transition-colors"
          >
            Coba Lagi
          </button>
        </div>
      )}

      {/* Reports Display Container */}
      <div className="rounded-2xl border border-slate-200/80 bg-white shadow-[0_2px_10px_-3px_rgba(6,78,59,0.05)] overflow-hidden">
        {/* Mobile View: Touch-Friendly Card List (No Horizontal Table Scroll) */}
        <div className="block md:hidden divide-y divide-slate-100">
          {isLoading ? (
            Array.from({ length: 3 }).map((_, idx) => (
              <div key={`mob-skel-${idx}`} className="p-4 space-y-3 animate-pulse">
                <div className="flex gap-3">
                  <div className="h-16 w-16 rounded-xl bg-slate-200 shrink-0" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-24 rounded bg-slate-200" />
                    <div className="h-4 w-44 rounded bg-slate-200" />
                    <div className="h-3 w-32 rounded bg-slate-100" />
                  </div>
                </div>
              </div>
            ))
          ) : displayedReports.length === 0 ? (
            <div className="py-12 px-4 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400 mx-auto mb-3">
                <Inbox className="h-6 w-6" />
              </div>
              <h3 className="font-sans text-sm font-bold text-slate-800">
                Tidak Ada Laporan Sampah Ditemukan
              </h3>
              <p className="mt-1 text-xs text-slate-500 max-w-xs mx-auto">
                {hasActiveFilters
                  ? 'Tidak ada laporan yang cocok dengan filter Anda.'
                  : 'Belum ada data laporan sampah warga yang tercatat.'}
              </p>
              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={handleResetFilters}
                  className="mt-3 inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-2xs"
                >
                  <RotateCcw className="h-3 w-3" />
                  <span>Reset Filter</span>
                </button>
              )}
            </div>
          ) : (
            displayedReports.map((report) => {
              const truncatedId = report.id.slice(0, 8).toUpperCase();
              const isImgError = imageErrors[report.id];
              const imgSrc = isImgError ? '/placeholder.png' : getFullImageUrl(report.image_url);

              return (
                <div
                  key={`mob-${report.id}`}
                  onClick={() => {
                    setSelectedReport(report);
                    setIsModalOpen(true);
                  }}
                  className="p-4 active:bg-slate-50 hover:bg-slate-50/60 transition-colors cursor-pointer space-y-2.5"
                >
                  <div className="flex gap-3">
                    {/* Thumbnail */}
                    <div className="w-16 h-16 rounded-xl border border-slate-200 overflow-hidden bg-slate-100 shrink-0">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={imgSrc}
                        alt={report.title}
                        className="w-full h-full object-cover"
                        onError={() => setImageErrors((prev) => ({ ...prev, [report.id]: true }))}
                      />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-1 mb-1">
                        <span className="font-mono text-[10px] font-bold text-slate-600 bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded">
                          SWMS-{truncatedId}
                        </span>
                        <StatusBadge status={report.status} size="sm" />
                      </div>

                      <h4 className="font-bold text-slate-900 text-xs sm:text-sm line-clamp-1">
                        {report.title}
                      </h4>

                      <div className="mt-1 flex items-center gap-1.5 flex-wrap">
                        <CategoryBadge category={report.category} size="sm" />
                        <span className="text-[11px] text-slate-500 truncate">
                          • {report.reporter?.full_name || 'Warga'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Location & Time Footer */}
                  <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-[11px] text-slate-500">
                    <div className="flex items-center gap-1 truncate max-w-[65%]">
                      <MapPin className="h-3 w-3 text-emerald-600 shrink-0" />
                      <span className="truncate">{report.address_note || `${report.latitude.toFixed(4)}, ${report.longitude.toFixed(4)}`}</span>
                    </div>
                    <span className="text-slate-400 font-medium shrink-0">
                      {formatRelativeTime(report.created_at)}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Desktop View: Full 9-Column Table */}
        <div className="hidden md:block overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/75 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                <th className="py-3.5 pl-5 pr-3">ID</th>
                <th className="py-3.5 px-3">Thumbnail</th>
                <th className="py-3.5 px-3 min-w-[180px]">Judul Laporan</th>
                <th className="py-3.5 px-3">Kategori</th>
                <th className="py-3.5 px-3">Pelapor</th>
                <th className="py-3.5 px-3 min-w-[200px]">Lokasi & Alamat</th>
                <th className="py-3.5 px-3">Waktu</th>
                <th className="py-3.5 px-3">Status</th>
                <th className="py-3.5 pl-3 pr-5 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans text-xs">
              {isLoading ? (
                // Loading Skeleton Rows
                Array.from({ length: 5 }).map((_, idx) => (
                  <tr key={`skeleton-${idx}`} className="animate-pulse">
                    <td className="py-4 pl-5 pr-3">
                      <div className="h-4 w-16 rounded bg-slate-200" />
                    </td>
                    <td className="py-4 px-3">
                      <div className="h-12 w-12 rounded-lg bg-slate-200" />
                    </td>
                    <td className="py-4 px-3">
                      <div className="space-y-2">
                        <div className="h-4 w-44 rounded bg-slate-200" />
                        <div className="h-3 w-28 rounded bg-slate-100" />
                      </div>
                    </td>
                    <td className="py-4 px-3">
                      <div className="h-6 w-24 rounded-md bg-slate-200" />
                    </td>
                    <td className="py-4 px-3">
                      <div className="h-4 w-20 rounded bg-slate-200" />
                    </td>
                    <td className="py-4 px-3">
                      <div className="h-4 w-28 rounded bg-slate-200" />
                    </td>
                    <td className="py-4 px-3">
                      <div className="h-4 w-20 rounded bg-slate-200" />
                    </td>
                    <td className="py-4 px-3">
                      <div className="h-6 w-20 rounded-md bg-slate-200" />
                    </td>
                    <td className="py-4 pl-3 pr-5 text-right">
                      <div className="h-8 w-16 ml-auto rounded-lg bg-slate-200" />
                    </td>
                  </tr>
                ))
              ) : reports.length === 0 ? (
                // Empty State
                <tr>
                  <td colSpan={9} className="py-16 text-center">
                    <div className="flex flex-col items-center justify-center">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400 mb-3">
                        <Inbox className="h-6 w-6" />
                      </div>
                      <h3 className="font-sans text-base font-semibold text-slate-800">
                        Tidak Ada Laporan Sampah Ditemukan
                      </h3>
                      <p className="mt-1 text-xs text-slate-500 max-w-sm">
                        {hasActiveFilters
                          ? 'Tidak ada laporan yang cocok dengan filter atau kata kunci pencarian Anda. Coba bersihkan filter.'
                          : 'Belum ada data laporan sampah warga yang tercatat di dalam sistem.'}
                      </p>
                      {hasActiveFilters && (
                        <button
                          type="button"
                          onClick={handleResetFilters}
                          className="mt-4 inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 active:scale-[0.98] transition-all shadow-2xs"
                        >
                          <RotateCcw className="h-3.5 w-3.5" />
                          <span>Bersihkan Filter</span>
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ) : (
                // Report Data Rows
                displayedReports.map((report) => {
                  const truncatedId = report.id.slice(0, 8).toUpperCase();
                  const isImgError = imageErrors[report.id];
                  const imgSrc = isImgError
                    ? '/placeholder.png'
                    : getFullImageUrl(report.image_url);

                  return (
                    <tr
                      key={report.id}
                      className="hover:bg-slate-50/80 transition-all duration-150 group"
                    >
                      {/* 1. ID */}
                      <td className="py-3.5 pl-5 pr-3">
                        <span className="font-mono text-xs font-medium text-slate-700 bg-slate-100/90 border border-slate-200/80 px-2 py-0.5 rounded-md">
                          SWMS-{truncatedId}
                        </span>
                      </td>

                      {/* 2. Thumbnail */}
                      <td className="py-3.5 px-3">
                        <div className="w-12 h-12 rounded-lg border border-slate-200 overflow-hidden bg-slate-100 shrink-0">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={imgSrc}
                            alt={report.title}
                            className="w-12 h-12 object-cover rounded-lg border border-slate-200"
                            onError={() =>
                              setImageErrors((prev) => ({ ...prev, [report.id]: true }))
                            }
                          />
                        </div>
                      </td>

                      {/* 3. Judul & Catatan */}
                      <td className="py-3.5 px-3">
                        <div className="font-medium text-slate-900 line-clamp-1">
                          {report.title}
                        </div>
                        <div className="text-xs text-slate-500 line-clamp-1 mt-0.5">
                          {/* In list items, address_note or reporter is shown */}
                          {report.reporter?.full_name ? `Pelapor: ${report.reporter.full_name}` : '-'}
                        </div>
                      </td>

                      {/* 4. Kategori */}
                      <td className="py-3.5 px-3">
                        <CategoryBadge category={report.category} size="sm" />
                      </td>

                      {/* 5. Pelapor */}
                      <td className="py-3.5 px-3 text-slate-700 font-medium whitespace-nowrap">
                        {report.reporter?.full_name || report.reporter?.email || 'Warga'}
                      </td>

                      {/* 6. Lokasi & Alamat */}
                      <td className="py-3.5 px-3 min-w-[200px]">
                        <div className="flex flex-col gap-1">
                          {report.address_note ? (
                            <span
                              className="font-semibold text-slate-800 line-clamp-1 flex items-center gap-1.5"
                              title={report.address_note}
                            >
                              <MapPin className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                              <span className="truncate">{report.address_note}</span>
                            </span>
                          ) : (
                            <span className="text-slate-400 italic text-[11px] flex items-center gap-1">
                              <MapPin className="h-3 w-3 text-slate-300" />
                              Alamat tersimpan di GPS
                            </span>
                          )}
                          <div className="flex items-center gap-1.5">
                            <span className="font-mono text-[11px] font-medium text-slate-600 bg-slate-100 border border-slate-200/80 px-1.5 py-0.5 rounded">
                              {report.latitude.toFixed(4)}, {report.longitude.toFixed(4)}
                            </span>
                            <a
                              href={getGoogleMapsUrl(report.latitude, report.longitude)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-0.5 text-[11px] font-semibold text-emerald-600 hover:text-emerald-700 hover:underline"
                              title="Buka titik koordinat di Google Maps"
                            >
                              <span>Peta</span>
                              <ExternalLink className="h-2.5 w-2.5" />
                            </a>
                          </div>
                        </div>
                      </td>

                      {/* 7. Waktu & Tanggal */}
                      <td className="py-3.5 px-3 text-xs whitespace-nowrap">
                        <div className="flex flex-col">
                          <span className="font-semibold text-slate-700">
                            {formatRelativeTime(report.created_at)}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono">
                            {formatDate(report.created_at)}
                          </span>
                        </div>
                      </td>

                      {/* 8. Status */}
                      <td className="py-3.5 px-3 whitespace-nowrap">
                        <StatusBadge status={report.status} size="sm" />
                      </td>

                      {/* 9. Aksi */}
                      <td className="py-3.5 pl-3 pr-5 text-right whitespace-nowrap">
                        <button
                          type="button"
                          onClick={() => handleOpenReviewModal(report)}
                          className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-2.5 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 hover:border-emerald-300 active:scale-[0.98] transition-all shadow-2xs group-hover:shadow-xs"
                        >
                          <Eye className="h-3.5 w-3.5" />
                          <span>Tinjau</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-200 bg-slate-50/50 px-5 py-3.5 text-xs text-slate-600">
          <div>
            <p className="font-medium text-slate-700">
              Halaman <span className="font-semibold text-slate-900">{page}</span> dari{' '}
              <span className="font-semibold text-slate-900">{totalPages || 1}</span>{' '}
              <span className="text-slate-400">|</span> Total{' '}
              <span className="font-semibold text-slate-900">{totalItems}</span> laporan
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
              disabled={page <= 1 || isLoading}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-2xs"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              <span>Sebelumnya</span>
            </button>
            <button
              type="button"
              onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={page >= totalPages || isLoading || totalPages === 0}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-2xs"
            >
              <span>Berikutnya</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Review Modal Dialog */}
      <ReportModal
        report={selectedReport}
        isOpen={isModalOpen}
        onClose={handleCloseReviewModal}
        onStatusUpdated={handleReportUpdated}
      />

      {/* Create Report Modal Dialog */}
      <CreateReportModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        categories={categories}
        onReportCreated={() => {
          fetchReports(true);
        }}
      />
    </div>
  );
}
