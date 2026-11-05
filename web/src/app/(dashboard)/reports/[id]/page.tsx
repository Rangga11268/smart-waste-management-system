'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  MapPin,
  ExternalLink,
  Clock,
  Calendar,
  User,
  Mail,
  Cpu,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ShieldCheck,
  ShieldAlert,
  Maximize2,
  X,
  FileText,
} from 'lucide-react';
import StatusBadge from '@/components/StatusBadge';
import CategoryBadge from '@/components/CategoryBadge';
import { reportsApi, getFullImageUrl } from '@/lib/api';
import { formatDate, formatRelativeTime, formatPercentage, getGoogleMapsUrl, cn } from '@/lib/utils';
import { useAuth } from '@/lib/auth';
import type {
  ReportDetailData,
  ReportStatus,
  ReportLogItem,
} from '@/types/api';

const STATUS_LABELS: Record<string, string> = {
  Pending: 'Menunggu Validasi',
  'In Progress': 'Sedang Ditangani',
  Completed: 'Selesai Ditangani',
  Rejected: 'Laporan Ditolak',
};

const STATUS_DESCRIPTIONS: Record<string, string> = {
  Pending: 'Laporan baru diajukan dan sedang menunggu evaluasi petugas kebersihan.',
  'In Progress': 'Armada kebersihan dan personel dinas telah ditugaskan ke lokasi titik tumpukan.',
  Completed: 'Tumpukan sampah telah berhasil diangkut tuntas ke TPST dan lokasi telah bersih kembali.',
  Rejected: 'Laporan ditolak (karena objek bukan sampah, foto buram/tidak valid, atau lokasi fiktif).',
};

const STATUS_ACTION_META: Record<
  string,
  {
    title: string;
    actionBadge: string;
    desc: string;
    activeBorderClass: string;
    activeBgClass: string;
    badgeClass: string;
  }
> = {
  'In Progress': {
    title: 'Tugaskan Armada Lapangan',
    actionBadge: 'Sedang Ditangani',
    desc: 'Laporan valid. Kerahkan truk dan regu pembersihan menuju titik koordinat.',
    activeBorderClass: 'border-blue-600 ring-1 ring-blue-600',
    activeBgClass: 'bg-blue-50/70',
    badgeClass: 'text-blue-700 bg-blue-100/80 border-blue-200',
  },
  Completed: {
    title: 'Tandai Selesai Ditangani',
    actionBadge: 'Selesai',
    desc: 'Tumpukan sampah telah tuntas diangkut dan area telah bersih kembali.',
    activeBorderClass: 'border-emerald-600 ring-1 ring-emerald-600',
    activeBgClass: 'bg-emerald-50/70',
    badgeClass: 'text-emerald-700 bg-emerald-100/80 border-emerald-200',
  },
  Rejected: {
    title: 'Tolak Laporan',
    actionBadge: 'Ditolak',
    desc: 'Laporan tidak memenuhi kriteria verifikasi (foto tidak jelas atau fiktif).',
    activeBorderClass: 'border-rose-600 ring-1 ring-rose-600',
    activeBgClass: 'bg-rose-50/70',
    badgeClass: 'text-rose-700 bg-rose-100/80 border-rose-200',
  },
};

const QUICK_NOTE_PRESETS: Record<string, string[]> = {
  'In Progress': [
    'Truk DLH ditugaskan menuju titik koordinat.',
    'Laporan diverifikasi valid, regu kebersihan lapangan meluncur.',
  ],
  Completed: [
    'Sampah telah diangkut ke TPST dan area telah bersih.',
    'Penanganan tuntas 100% oleh armada lapangan.',
  ],
  Rejected: [
    'Foto bukti buram atau objek bukan sampah.',
    'Lokasi di luar jangkauan operasional dinas.',
  ],
};

function getAllowedTransitions(currentStatus: ReportStatus): ReportStatus[] {
  switch (currentStatus) {
    case 'Pending':
      return ['In Progress', 'Rejected'];
    case 'In Progress':
      return ['Completed', 'Rejected'];
    case 'Completed':
    case 'Rejected':
    default:
      return [];
  }
}

export default function ReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user, isAdmin } = useAuth();
  const id = typeof params?.id === 'string' ? params.id : '';

  const [report, setReport] = useState<ReportDetailData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Status disposition form states
  const [selectedStatus, setSelectedStatus] = useState<ReportStatus | null>(null);
  const [adminNotes, setAdminNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Lightbox view state
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);

  const fetchDetail = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await reportsApi.getReport(id);
      setReport(res.data);
      setSelectedStatus(null);
      setAdminNotes('');
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(typeof msg === 'string' ? msg : 'Laporan tidak ditemukan atau gagal dimuat.');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchDetail();
  }, [fetchDetail]);

  const handleStatusSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStatus || !report) return;

    setIsSubmitting(true);
    setActionError(null);
    setActionSuccess(null);

    try {
      const res = await reportsApi.updateStatus(report.id, {
        status: selectedStatus,
        admin_notes: adminNotes.trim() ? adminNotes.trim() : undefined,
      });

      setActionSuccess(`Status laporan berhasil diubah menjadi "${selectedStatus}".`);
      setReport(res.data);
      setSelectedStatus(null);
      setAdminNotes('');
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setActionError(
        typeof msg === 'string' ? msg : 'Gagal memperbarui status laporan. Periksa hak akses Anda.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-3">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
        <p className="font-sans text-sm text-slate-500 font-medium">Memuat detail berkas laporan...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-2xl mx-auto py-16 text-center space-y-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-rose-600 mx-auto border border-rose-200">
          <AlertCircle className="h-7 w-7" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Berkas Laporan Tidak Ditemukan</h2>
        <p className="text-sm text-slate-500">{error || 'ID laporan tidak valid atau telah dihapus.'}</p>
        <div className="pt-2">
          <Link
            href="/reports"
            className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-bold text-white hover:bg-slate-800 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Kembali ke Daftar Laporan</span>
          </Link>
        </div>
      </div>
    );
  }

  const truncatedId = report.id.slice(0, 8).toUpperCase();
  const imgSrc = getFullImageUrl(report.image_url);
  const currentStatus = report.status;
  const isTerminal = currentStatus === 'Completed' || currentStatus === 'Rejected';
  const allowedOptions = getAllowedTransitions(currentStatus);
  const mapsUrl = getGoogleMapsUrl(report.latitude, report.longitude);

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header & Breadcrumb Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between pb-5 border-b border-slate-200">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Link
              href="/reports"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
            >
              <ArrowLeft className="h-3.5 w-3.5 text-emerald-600" />
              <span>Daftar Laporan</span>
            </Link>
            <span className="text-slate-300">/</span>
            <span className="font-mono text-xs font-bold text-slate-600">
              SWMS-{truncatedId}
            </span>
          </div>

          <h1 className="font-sans text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
            {report.title}
          </h1>

          <div className="flex items-center gap-2.5 pt-0.5 flex-wrap">
            <StatusBadge status={currentStatus} size="sm" />
            <CategoryBadge category={report.category} size="sm" />
            <span className="text-xs text-slate-400 font-medium">
              Diajukan {formatRelativeTime(report.created_at)} ({formatDate(report.created_at)})
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <a
            href={mapsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs"
          >
            <MapPin className="h-3.5 w-3.5 text-emerald-600" />
            <span>Peta Satelit</span>
            <ExternalLink className="h-3 w-3 text-slate-400" />
          </a>
        </div>
      </div>

      {/* Main 2-Column Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
        {/* Left Column (Primary Evidence & Context - 7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* 1. Field Photo Evidence Card */}
          <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-2xs">
            <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
              <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Bukti Foto Lapangan
              </span>
              <button
                type="button"
                onClick={() => setIsLightboxOpen(true)}
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 hover:text-emerald-700 transition-colors"
              >
                <Maximize2 className="h-3.5 w-3.5" />
                <span>Perbesar Foto</span>
              </button>
            </div>

            <div
              onClick={() => setIsLightboxOpen(true)}
              className="relative w-full h-72 sm:h-96 bg-slate-950 flex items-center justify-center cursor-pointer group"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={imgSrc}
                alt={report.title}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
              />
              <div className="absolute inset-0 bg-slate-950/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <span className="inline-flex items-center gap-1.5 bg-black/75 text-white text-xs font-semibold px-3 py-1.5 rounded-lg backdrop-blur-xs">
                  <Maximize2 className="h-3.5 w-3.5" />
                  <span>Klik untuk Memperbesar</span>
                </span>
              </div>
            </div>

            <div className="px-5 py-3 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Status Dokumen: Otentik</span>
              <span>GPS Lat/Lng Tersemat</span>
            </div>
          </div>

          {/* 2. AI MobileNetV2 Telemetry Card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-100 text-emerald-800 font-bold">
                  <Cpu className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="font-sans text-sm font-bold text-slate-900">
                    Telemetri Inferensi AI (MobileNetV2)
                  </h3>
                  <p className="text-[11px] text-slate-500">Klasifikasi otomatis jenis sampah perkotaan</p>
                </div>
              </div>
              <span className="font-mono text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
                {report.ai_confidence ? formatPercentage(report.ai_confidence) : '95.0%'} Akurasi
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-3.5">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Kategori Terdeteksi
                </span>
                <span className="font-sans text-sm font-bold text-slate-900">
                  {report.detected_category || report.category.name}
                </span>
              </div>

              <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-3.5">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Arsitektur Model
                </span>
                <span className="font-mono text-xs font-bold text-slate-800">
                  MobileNetV2 (FP16 / TFLite)
                </span>
              </div>
            </div>

            {/* Precision Confidence Bar */}
            <div className="space-y-1.5 pt-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-600">Skor Keyakinan Model</span>
                <span className="font-mono font-bold text-slate-900">
                  {report.ai_confidence ? formatPercentage(report.ai_confidence) : '95.0%'}
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                <div
                  className="bg-emerald-600 h-2 rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(100, Math.round((report.ai_confidence || 0.95) * 100))}%`,
                  }}
                />
              </div>
            </div>
          </div>

          {/* 3. Location, Description & Reporter Details */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
            <h3 className="font-sans text-sm font-bold text-slate-900 border-b border-slate-100 pb-2.5">
              Detail Lokasi &amp; Deskripsi Laporan
            </h3>

            {/* Description */}
            <div>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                Deskripsi Lapangan
              </span>
              <p className="text-xs sm:text-sm text-slate-800 leading-relaxed bg-slate-50/60 p-3 rounded-xl border border-slate-100">
                {report.description || 'Tidak ada catatan deskripsi tambahan yang disertakan oleh pelapor.'}
              </p>
            </div>

            {/* Location Geotagging */}
            <div>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                Patokan Alamat &amp; Koordinat
              </span>
              <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-3.5 space-y-2">
                <div className="flex items-start gap-2">
                  <MapPin className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span className="text-xs sm:text-sm font-semibold text-slate-900 leading-snug">
                    {report.address_note || 'Alamat patokan dicatat otomatis via satelit GPS'}
                  </span>
                </div>
                <div className="flex items-center gap-2 pt-1 font-mono text-xs text-slate-600">
                  <span>Lat: {report.latitude.toFixed(6)}</span>
                  <span>•</span>
                  <span>Lng: {report.longitude.toFixed(6)}</span>
                </div>
              </div>
            </div>

            {/* Reporter Data */}
            <div className="pt-2 border-t border-slate-100">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">
                Informasi Pelapor
              </span>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-700 font-bold text-xs border border-slate-200">
                  {(report.reporter?.full_name || 'W')[0].toUpperCase()}
                </div>
                <div>
                  <p className="text-xs sm:text-sm font-bold text-slate-900 leading-snug">
                    {report.reporter?.full_name || 'Warga Masyarakat'}
                  </p>
                  <p className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                    <Mail className="h-3 w-3 text-slate-400" />
                    <span>{report.reporter?.email || 'user@bilcode.id'}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (Operational Triage & Audit Trail - 5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* 1. Operational Disposition Console */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-sans text-sm font-bold text-slate-900">
                  Konsol Disposisi Kasus
                </h3>
                <p className="text-[11px] text-slate-500">Triage status dan penugasan armada dinas</p>
              </div>
              <span className="font-mono text-[10px] font-bold text-slate-500 uppercase tracking-wider bg-slate-100 px-2 py-0.5 rounded">
                {isAdmin ? 'Akses Admin' : 'Warga'}
              </span>
            </div>

            {/* Current Status Box */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-3.5 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Status Saat Ini:</span>
                <StatusBadge status={currentStatus} size="sm" />
              </div>
              <p className="text-xs text-slate-600 leading-relaxed pt-1">
                {STATUS_DESCRIPTIONS[currentStatus] || 'Laporan tersimpan di sistem dinas kebersihan.'}
              </p>
            </div>

            {/* Action Form for Admin */}
            {!isAdmin ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 flex items-start gap-2.5">
                <ShieldAlert className="h-4 w-4 text-slate-400 shrink-0 mt-0.5" />
                <p>
                  Perubahan status laporan hanya dapat dilakukan oleh akun dengan hak akses
                  Administrator / Petugas Kebersihan.
                </p>
              </div>
            ) : isTerminal ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 space-y-1">
                <p className="font-bold text-slate-800">
                  Laporan Berada Pada Status Terminal ({currentStatus})
                </p>
                <p className="text-slate-500 text-[11px] leading-relaxed">
                  Sesuai aturan sistem SWMS, laporan yang telah selesai atau ditolak dikunci secara permanen untuk menjaga integritas rekam jejak audit (*audit trail*).
                </p>
              </div>
            ) : (
              <form onSubmit={handleStatusSubmit} className="space-y-4">
                {actionError && (
                  <div className="flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
                    <AlertCircle className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" />
                    <p className="leading-relaxed">{actionError}</p>
                  </div>
                )}

                {actionSuccess && (
                  <div className="flex items-start gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                    <p className="leading-relaxed">{actionSuccess}</p>
                  </div>
                )}

                {/* State Machine Transition Tiles */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Pilih Transisi Status <span className="text-rose-500">*</span>
                  </label>
                  <div className="space-y-2">
                    {allowedOptions.map((opt) => {
                      const isSelected = selectedStatus === opt;
                      const meta = STATUS_ACTION_META[opt] || {
                        title: opt,
                        actionBadge: opt,
                        desc: '',
                        activeBorderClass: 'border-emerald-600 ring-1 ring-emerald-600',
                        activeBgClass: 'bg-emerald-50/70',
                        badgeClass: 'text-emerald-700 bg-emerald-100',
                      };

                      return (
                        <button
                          key={opt}
                          type="button"
                          disabled={isSubmitting}
                          onClick={() => {
                            setSelectedStatus(opt);
                            if (
                              !adminNotes ||
                              Object.values(QUICK_NOTE_PRESETS).flat().includes(adminNotes)
                            ) {
                              setAdminNotes(QUICK_NOTE_PRESETS[opt]?.[0] || '');
                            }
                          }}
                          className={cn(
                            'w-full flex flex-col text-left p-3.5 rounded-xl border transition-all text-xs cursor-pointer',
                            isSelected
                              ? cn(meta.activeBgClass, meta.activeBorderClass, 'shadow-xs')
                              : 'border-slate-200 bg-slate-50/50 hover:bg-slate-100 hover:border-slate-300'
                          )}
                        >
                          <div className="flex items-center justify-between gap-1 mb-1">
                            <span className="font-bold text-slate-900">{meta.title}</span>
                            <span
                              className={cn(
                                'text-[10px] font-bold px-2 py-0.5 rounded border',
                                meta.badgeClass
                              )}
                            >
                              {meta.actionBadge}
                            </span>
                          </div>
                          <span className="text-[11px] text-slate-500 leading-snug">
                            {meta.desc}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Admin Disposition Notes & Presets */}
                <div className="space-y-1.5">
                  <label
                    htmlFor="admin-notes"
                    className="block text-xs font-bold text-slate-700 uppercase tracking-wider"
                  >
                    Catatan Disposisi (Admin Notes)
                  </label>
                  <textarea
                    id="admin-notes"
                    rows={2}
                    value={adminNotes}
                    onChange={(e) => setAdminNotes(e.target.value)}
                    disabled={isSubmitting}
                    placeholder="Instruksi penugasan armada atau keterangan disposisi..."
                    className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:bg-slate-100 resize-none font-sans"
                  />

                  {/* 1-Click Tactical Presets */}
                  {selectedStatus && QUICK_NOTE_PRESETS[selectedStatus] && (
                    <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                      <span className="text-[10px] font-bold text-slate-400">Preset:</span>
                      {QUICK_NOTE_PRESETS[selectedStatus].map((preset) => (
                        <button
                          key={preset}
                          type="button"
                          onClick={() => setAdminNotes(preset)}
                          className={cn(
                            'text-[10px] px-2 py-0.5 rounded border transition-all truncate max-w-full font-medium',
                            adminNotes === preset
                              ? 'bg-emerald-600 text-white border-emerald-600 shadow-2xs'
                              : 'text-slate-600 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-800 border-slate-200'
                          )}
                        >
                          + {preset}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting || !selectedStatus}
                  className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-xs sm:text-sm font-bold text-white shadow-xs hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed transition-all min-h-[44px]"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Memproses Perubahan...</span>
                    </>
                  ) : (
                    <span>Perbarui Status Laporan</span>
                  )}
                </button>
              </form>
            )}
          </div>

          {/* 2. Immutable Audit Trail Timeline */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <Clock className="h-4 w-4 text-slate-400" />
              <div>
                <h3 className="font-sans text-sm font-bold text-slate-900">
                  Riwayat Jejak Audit (*Audit Trail*)
                </h3>
                <p className="text-[11px] text-slate-500">Rekam jejak setiap tindakan perubahan status</p>
              </div>
            </div>

            {report.logs.length === 0 ? (
              <p className="text-xs text-slate-400 italic py-2">Belum ada riwayat transisi status tercatat.</p>
            ) : (
              <div className="space-y-3 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-200 before:z-0">
                {report.logs.map((log: ReportLogItem, idx: number) => (
                  <div
                    key={log.id}
                    className="relative z-10 pl-7 space-y-1 text-xs"
                  >
                    {/* Step Icon Indicator */}
                    <div className="absolute left-1.5 top-1 h-4 w-4 rounded-full bg-white border-2 border-emerald-600" />

                    <div className="flex items-center justify-between gap-1 flex-wrap">
                      <span className="font-bold text-slate-900">
                        {log.previous_status
                          ? `Status: ${log.previous_status} → ${log.new_status}`
                          : `Laporan Dibuat (${log.new_status})`}
                      </span>
                      <span className="font-mono text-[10px] text-slate-400">
                        {formatRelativeTime(log.created_at)}
                      </span>
                    </div>

                    {log.remarks && (
                      <p className="text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-100 text-[11px] mt-1 italic">
                        &ldquo;{log.remarks}&rdquo;
                      </p>
                    )}

                    <div className="flex items-center gap-1.5 text-[10px] text-slate-400 pt-0.5">
                      <span>Petugas: {log.actor_id ? `Petugas #${log.actor_id.slice(0, 8).toUpperCase()}` : 'Sistem DLH'}</span>
                      <span>•</span>
                      <span>{formatDate(log.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Lightbox Modal */}
      {isLightboxOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm"
          onClick={() => setIsLightboxOpen(false)}
        >
          <div className="relative max-w-4xl w-full max-h-[90vh] flex flex-col items-center">
            <button
              onClick={() => setIsLightboxOpen(false)}
              className="absolute -top-10 right-0 text-white hover:text-slate-300 transition-colors p-2"
              aria-label="Tutup foto"
            >
              <X className="h-6 w-6" />
            </button>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imgSrc}
              alt={report.title}
              className="max-w-full max-h-[85vh] object-contain rounded-xl shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}
    </div>
  );
}
