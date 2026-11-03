'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  X,
  ExternalLink,
  MapPin,
  Sparkles,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldAlert,
  Maximize2,
} from 'lucide-react';
import StatusBadge from '@/components/StatusBadge';
import CategoryBadge from '@/components/CategoryBadge';
import { reportsApi, getFullImageUrl } from '@/lib/api';
import { formatDate, formatRelativeTime, formatPercentage, cn } from '@/lib/utils';
import { useAuth } from '@/lib/auth';
import type {
  ReportDetailData,
  ReportListItem,
  ReportStatus,
  ReportLogItem,
} from '@/types/api';

export interface ReportModalProps {
  report: ReportDetailData | ReportListItem | null;
  isOpen: boolean;
  onClose: () => void;
  onStatusUpdated?: (updatedReport: ReportDetailData) => void;
}

export default function ReportModal({
  report,
  isOpen,
  onClose,
  onStatusUpdated,
}: ReportModalProps) {
  const { isAdmin } = useAuth();

  const [detail, setDetail] = useState<ReportDetailData | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState<boolean>(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  // Status update form states
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [adminNotes, setAdminNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Image fallback state
  const [imgSrc, setImgSrc] = useState<string>('/placeholder.png');
  const [isLightboxOpen, setIsLightboxOpen] = useState<boolean>(false);

  // Load detailed report data on open
  const fetchReportDetail = useCallback(async (reportId: string) => {
    setIsLoadingDetail(true);
    setDetailError(null);
    try {
      const res = await reportsApi.getReport(reportId);
      setDetail(res.data);
      if (res.data.image_url) {
        setImgSrc(getFullImageUrl(res.data.image_url));
      }
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setDetailError(typeof msg === 'string' ? msg : 'Gagal memuat detail laporan.');
    } finally {
      setIsLoadingDetail(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen && report?.id) {
      setActionError(null);
      setActionSuccess(null);
      setSelectedStatus('');
      setAdminNotes('');
      if (report.image_url) {
        setImgSrc(getFullImageUrl(report.image_url));
      }
      fetchReportDetail(report.id);
    } else {
      setDetail(null);
    }
  }, [isOpen, report?.id, report?.image_url, fetchReportDetail]);

  // Handle ESC key to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !report) return null;

  // Active report merged from detail or partial report
  const currentStatus = (detail?.status || report.status) as ReportStatus;
  const isTerminal = currentStatus === 'Completed' || currentStatus === 'Rejected';

  // Allowed transitions per state machine rules
  const getAllowedOptions = (status: ReportStatus): ReportStatus[] => {
    if (status === 'Pending') return ['In Progress', 'Rejected'];
    if (status === 'In Progress') return ['Completed', 'Rejected'];
    return [];
  };
  const allowedOptions = getAllowedOptions(currentStatus);

  // Form submission handler
  const handleStatusSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStatus) {
      setActionError('Silakan pilih status baru terlebih dahulu.');
      return;
    }

    setIsSubmitting(true);
    setActionError(null);
    setActionSuccess(null);

    try {
      const res = await reportsApi.updateStatus(report.id, {
        status: selectedStatus as ReportStatus,
        admin_notes: adminNotes.trim() ? adminNotes.trim() : undefined,
      });

      const updatedData = res.data;
      setActionSuccess(`Status berhasil diubah menjadi "${selectedStatus}".`);
      setSelectedStatus('');
      setAdminNotes('');

      // Refresh detailed report data to capture new audit trail logs
      await fetchReportDetail(report.id);

      // Notify parent table
      if (onStatusUpdated) {
        onStatusUpdated(updatedData);
      }
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setActionError(
        typeof msg === 'string'
          ? msg
          : 'Terjadi kesalahan saat memperbarui status laporan.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const truncatedId = report.id ? report.id.slice(0, 8).toUpperCase() : 'UNKNOWN';
  const latitude = detail?.latitude ?? report.latitude;
  const longitude = detail?.longitude ?? report.longitude;
  const mapsUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;
  const logs: ReportLogItem[] = detail?.logs ?? [];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby="report-modal-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden my-6 max-h-[92vh] flex flex-col animate-in fade-in zoom-in-95 duration-200">
        {/* Modal Header */}
        <div className="flex items-start justify-between border-b border-slate-200 px-5 py-4 sm:px-6 bg-slate-50/50">
          <div className="space-y-1 pr-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs font-semibold text-slate-500 bg-slate-200/80 px-2 py-0.5 rounded">
                #RPT-{truncatedId}
              </span>
              <StatusBadge status={currentStatus} size="sm" />
            </div>
            <h2
              id="report-modal-title"
              className="font-heading text-lg sm:text-xl font-bold text-slate-900 tracking-tight"
            >
              {detail?.title || report.title}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-200/60 hover:text-slate-700 transition-colors shrink-0"
            aria-label="Tutup modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-5">
          {/* Photo Evidence Preview */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Bukti Foto Sampah
              </label>
              <button
                type="button"
                onClick={() => setIsLightboxOpen(true)}
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 hover:text-emerald-700 transition-colors"
              >
                <Maximize2 className="h-3 w-3" />
                <span>Perbesar Foto</span>
              </button>
            </div>
            <div
              onClick={() => setIsLightboxOpen(true)}
              className="group relative w-full h-56 sm:h-64 rounded-xl overflow-hidden border border-slate-200/90 bg-slate-100 flex items-center justify-center cursor-pointer shadow-inner"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={imgSrc}
                alt={report.title}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                onError={() => setImgSrc('/placeholder.png')}
              />
              <div className="absolute inset-0 bg-slate-900/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <span className="inline-flex items-center gap-1.5 bg-slate-900/80 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow-lg backdrop-blur-xs">
                  <Maximize2 className="h-3.5 w-3.5" />
                  <span>Klik untuk Memperbesar</span>
                </span>
              </div>
            </div>
          </div>

          {/* AI Classification & Confidence Badge */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-emerald-50/70 border border-emerald-200/80 rounded-xl shadow-[0_2px_10px_-3px_rgba(6,78,59,0.05)]">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-xs">
                <Sparkles className="h-4 w-4" />
              </div>
              <div>
                <p className="text-[11px] font-semibold text-emerald-800 uppercase tracking-wider">
                  Deteksi Kategori AI
                </p>
                <div className="mt-1">
                  <CategoryBadge
                    category={detail?.detected_category || detail?.category || report.category}
                    size="sm"
                  />
                </div>
              </div>
            </div>
            <div className="sm:text-right pl-12 sm:pl-0 border-t sm:border-t-0 pt-2 sm:pt-0 border-emerald-200/50">
              <p className="text-[11px] font-medium text-slate-500">Tingkat Keyakinan (Confidence)</p>
              <div className="mt-1">
                <span className="font-mono text-xs font-semibold text-emerald-800 bg-white/90 border border-emerald-200/80 px-2 py-0.5 rounded-md">
                  {formatPercentage(detail?.ai_confidence ?? 0)}
                </span>
              </div>
            </div>
          </div>

          {/* Geolocation & Maps Integration */}
          <div className="rounded-xl border border-emerald-100 bg-emerald-50/40 p-4 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
              <div className="space-y-2 flex-1">
                <div className="flex items-start gap-2 text-xs">
                  <MapPin className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-slate-900 block text-sm">
                      {detail?.address_note || (report as any)?.address_note || 'Alamat Lapangan'}
                    </span>
                    <span className="font-mono text-xs text-slate-500 mt-0.5 inline-block">
                      Koordinat: {typeof latitude === 'number' ? latitude.toFixed(6) : latitude}, {typeof longitude === 'number' ? longitude.toFixed(6) : longitude}
                    </span>
                  </div>
                </div>
                {detail?.description && (
                  <p className="text-xs text-slate-600 pl-6 border-t border-emerald-100/60 pt-2 mt-2">
                    <span className="font-semibold text-slate-700">Keterangan:</span> {detail.description}
                  </p>
                )}
              </div>
              <a
                href={mapsUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-300 active:scale-[0.98] shadow-xs transition-all shrink-0"
              >
                <span>Buka Google Maps</span>
                <ExternalLink className="h-3.5 w-3.5 text-emerald-600" />
              </a>
            </div>
          </div>

          {/* Pelapor & Waktu Info */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-600 bg-white p-3.5 rounded-xl border border-slate-200">
            <div>
              <span className="font-medium text-slate-500">Pelapor:</span>{' '}
              <span className="font-semibold text-slate-800">
                {detail?.reporter?.full_name || report.reporter?.full_name || report.reporter?.email || 'Warga'}
              </span>
            </div>
            <div>
              <span className="font-medium text-slate-500">Waktu Lapor:</span>{' '}
              <span className="text-slate-800 font-medium">
                {formatRelativeTime(report.created_at)}{' '}
                <span className="text-[11px] text-slate-400">({formatDate(report.created_at)})</span>
              </span>
            </div>
          </div>

          {/* State Machine Disposition Action Form (Admin only) */}
          <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-3.5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <h3 className="font-heading text-sm font-bold text-slate-900">
                Disposisi Status Laporan
              </h3>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                Khusus Admin
              </span>
            </div>

            {!isAdmin ? (
              <div className="flex items-center gap-2.5 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
                <ShieldAlert className="h-4 w-4 text-slate-400 shrink-0" />
                <p>
                  Perubahan status laporan hanya dapat dilakukan oleh akun dengan hak akses
                  Administrator.
                </p>
              </div>
            ) : isTerminal ? (
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3.5 text-xs text-slate-600 space-y-1">
                <p className="font-semibold text-slate-800">
                  Laporan telah selesai/ditutup (Status Terminal). Tidak dapat diubah lagi.
                </p>
                <p className="text-slate-500 text-[11px]">
                  Status saat ini adalah <span className="font-semibold">{currentStatus}</span>. Aturan sistem SWMS mengunci status terminal untuk menjaga integritas audit trail.
                </p>
              </div>
            ) : (
              <form onSubmit={handleStatusSubmit} className="space-y-3">
                {actionError && (
                  <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
                    <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
                    <p>{actionError}</p>
                  </div>
                )}

                {actionSuccess && (
                  <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800">
                    <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
                    <p>{actionSuccess}</p>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label
                      htmlFor="status-select"
                      className="block text-xs font-semibold text-slate-700 mb-1"
                    >
                      Pilih Status Baru <span className="text-rose-500">*</span>
                    </label>
                    <select
                      id="status-select"
                      value={selectedStatus}
                      onChange={(e) => setSelectedStatus(e.target.value)}
                      disabled={isSubmitting}
                      className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:bg-slate-100"
                    >
                      <option value="">-- Pilih Transisi Status --</option>
                      {allowedOptions.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label
                      htmlFor="admin-notes"
                      className="block text-xs font-semibold text-slate-700 mb-1"
                    >
                      Catatan Disposisi (Admin Notes)
                    </label>
                    <textarea
                      id="admin-notes"
                      rows={2}
                      value={adminNotes}
                      onChange={(e) => setAdminNotes(e.target.value)}
                      disabled={isSubmitting}
                      placeholder="Instruksi penugasan armada atau alasan disposisi..."
                      className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:bg-slate-100 resize-none"
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-1">
                  <button
                    type="submit"
                    disabled={isSubmitting || !selectedStatus}
                    className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isSubmitting && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                    <span>Perbarui Status</span>
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Audit Trail History Timeline */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
              <Clock className="h-4 w-4 text-slate-400" />
              <h3 className="font-heading text-sm font-bold text-slate-900">
                Riwayat Jejak Audit (Audit Trail)
              </h3>
            </div>

            {isLoadingDetail ? (
              <div className="flex items-center justify-center py-6 text-xs text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Memuat riwayat audit...
              </div>
            ) : detailError ? (
              <p className="text-xs text-rose-600">{detailError}</p>
            ) : logs.length === 0 ? (
              <p className="text-xs text-slate-400 italic">Belum ada riwayat status tercatat.</p>
            ) : (
              <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {logs.map((log) => (
                  <div key={log.id} className="relative">
                    <span className="absolute -left-6 top-1 h-3 w-3 rounded-full border-2 border-white bg-emerald-500 shadow-xs" />
                    <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-2.5 text-xs space-y-1">
                      <div className="flex flex-wrap items-center justify-between gap-1">
                        <div className="flex items-center gap-1.5 font-semibold text-slate-800">
                          {log.previous_status ? (
                            <>
                              <span className="text-slate-500">{log.previous_status}</span>
                              <ArrowRight className="h-3 w-3 text-slate-400" />
                              <span className="text-emerald-700">{log.new_status}</span>
                            </>
                          ) : (
                            <span className="text-emerald-700">Status Awal: {log.new_status}</span>
                          )}
                        </div>
                        <span className="font-mono text-[11px] text-slate-400">
                          {formatDate(log.created_at)}
                        </span>
                      </div>
                      {log.remarks && (
                        <p className="text-slate-600 pt-0.5">
                          <span className="font-medium text-slate-700">Catatan:</span> {log.remarks}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-end border-t border-slate-200 bg-slate-50 px-5 py-3 sm:px-6">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 hover:text-slate-900 active:scale-[0.98] transition-all shadow-xs"
          >
            Tutup
          </button>
        </div>
      </div>

      {/* Lightbox / Zoom Overlay */}
      {isLightboxOpen && (
        <div
          className="fixed inset-0 z-60 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setIsLightboxOpen(false)}
        >
          <div className="relative max-w-4xl max-h-[90vh] flex flex-col items-center">
            <button
              type="button"
              onClick={() => setIsLightboxOpen(false)}
              className="absolute -top-12 right-0 rounded-full bg-white/20 p-2 text-white hover:bg-white/30 transition-colors"
              aria-label="Tutup foto perbesar"
            >
              <X className="h-6 w-6" />
            </button>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imgSrc}
              alt={report.title}
              className="max-w-full max-h-[85vh] object-contain rounded-xl shadow-2xl border border-white/10"
            />
            <p className="mt-3 text-xs text-white/80 font-medium">
              {report.title} — Klik di mana saja untuk menutup
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
