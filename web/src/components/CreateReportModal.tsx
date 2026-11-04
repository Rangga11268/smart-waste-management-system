'use client';

import React, { useState, useRef } from 'react';
import {
  X,
  Upload,
  MapPin,
  Sparkles,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Navigation,
} from 'lucide-react';
import { reportsApi, predictApi } from '@/lib/api';
import { formatPercentage, cn } from '@/lib/utils';
import type { WasteCategory, PredictResponseData } from '@/types/api';

export interface CreateReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  categories: WasteCategory[];
  onReportCreated: () => void;
}

export default function CreateReportModal({
  isOpen,
  onClose,
  categories,
  onReportCreated,
}: CreateReportModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [addressNote, setAddressNote] = useState('');
  const [latitude, setLatitude] = useState<string>('-6.2088');
  const [longitude, setLongitude] = useState<string>('106.8456');
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | ''>('');

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // AI inference state
  const [isPredicting, setIsPredicting] = useState(false);
  const [aiPrediction, setAiPrediction] = useState<PredictResponseData | null>(null);

  // Form submission state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [isLocating, setIsLocating] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    setAiPrediction(null);
    setFormError(null);

    // Automatically trigger AI classification
    setIsPredicting(true);
    try {
      const res = await predictApi.predict(file);
      setAiPrediction(res.data);

      // Auto-select category if matching category name exists
      const predictedName = res.data.category.toLowerCase();
      const matched = categories.find((c) =>
        c.name.toLowerCase().includes(predictedName) || predictedName.includes(c.name.toLowerCase())
      );
      if (matched) {
        setSelectedCategoryId(matched.id);
      }
    } catch {
      // AI failure shouldn't block report submission
      console.warn('AI preview unavailable');
    } finally {
      setIsPredicting(false);
    }
  };

  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      setFormError('Browser tidak mendukung geolokasi GPS.');
      return;
    }
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        setLatitude(lat.toFixed(6));
        setLongitude(lon.toFixed(6));
        try {
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18`
          );
          if (res.ok) {
            const data = await res.json();
            if (data?.display_name && !addressNote) {
              setAddressNote(data.display_name);
            }
          }
        } catch (_) {}
        setIsLocating(false);
      },
      () => {
        setFormError('Gagal mendapatkan lokasi GPS. Pastikan izin lokasi aktif.');
        setIsLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setFormError('Judul laporan wajib diisi.');
      return;
    }
    if (!selectedFile) {
      setFormError('Bukti foto sampah wajib diunggah.');
      return;
    }

    const latNum = parseFloat(latitude);
    const lngNum = parseFloat(longitude);
    if (isNaN(latNum) || isNaN(lngNum)) {
      setFormError('Koordinat GPS tidak valid.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      const formData = new FormData();
      formData.append('title', title.trim());
      formData.append('latitude', latNum.toString());
      formData.append('longitude', lngNum.toString());
      if (description.trim()) formData.append('description', description.trim());
      if (addressNote.trim()) formData.append('address_note', addressNote.trim());
      if (selectedCategoryId) formData.append('category_id', selectedCategoryId.toString());
      formData.append('image', selectedFile);

      await reportsApi.createReport(formData);

      // Reset and close
      onReportCreated();
      onClose();
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setFormError(typeof msg === 'string' ? msg : 'Gagal mengirim laporan. Periksa koneksi backend.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto"
      role="dialog"
      aria-modal="true"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isSubmitting) onClose();
      }}
    >
      <div className="relative w-full max-w-xl bg-white rounded-t-3xl sm:rounded-2xl shadow-2xl border-t sm:border border-slate-200/90 overflow-hidden max-h-[92vh] sm:max-h-[90vh] flex flex-col animate-in slide-in-from-bottom duration-300 sm:zoom-in-95 sm:duration-150 sm:my-6">
        {/* Mobile Bottom Sheet Drag Handle */}
        <div className="w-full pt-2.5 pb-1 flex justify-center sm:hidden bg-slate-50/70 cursor-grab">
          <div className="w-12 h-1.5 rounded-full bg-slate-300" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 sm:px-6 bg-slate-50/70">
          <div>
            <h2 className="font-sans text-lg font-bold text-slate-900">
              Buat Laporan Sampah Baru
            </h2>
            <p className="font-sans text-xs text-slate-500">
              Laporkan tumpukan sampah perkotaan dengan bantuan klasifikasi AI
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-200/60 hover:text-slate-700 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Form Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-4">
          {formError && (
            <div className="flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
              <p className="font-medium">{formError}</p>
            </div>
          )}

          {/* Photo Upload Area */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-700">
              Foto Bukti Sampah <span className="text-rose-500">*</span>
            </label>
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            {previewUrl ? (
              <div className="relative w-full h-48 rounded-xl overflow-hidden border border-slate-200 bg-slate-100 flex items-center justify-center group">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="absolute inset-0 bg-slate-900/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold gap-1.5"
                >
                  <Upload className="h-4 w-4" />
                  <span>Ganti Foto</span>
                </button>
              </div>
            ) : (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="w-full h-36 rounded-xl border-2 border-dashed border-slate-300 hover:border-emerald-500 bg-slate-50/60 hover:bg-emerald-50/20 transition-all cursor-pointer flex flex-col items-center justify-center p-4 text-center"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 mb-2">
                  <Upload className="h-5 w-5" />
                </div>
                <p className="text-xs font-semibold text-slate-700">Klik untuk unggah foto sampah</p>
                <p className="text-[11px] text-slate-400 mt-0.5">JPG, PNG atau WebP (Maks 10MB)</p>
              </div>
            )}
          </div>

          {/* AI Detection Banner */}
          {isPredicting ? (
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-emerald-50/80 border border-emerald-200 text-xs text-emerald-800">
              <Loader2 className="h-4 w-4 animate-spin text-emerald-600 shrink-0" />
              <span>AI MobileNetV2 sedang menganalisis foto sampah...</span>
            </div>
          ) : aiPrediction ? (
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs shadow-xs">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-emerald-600 shrink-0" />
                <div>
                  <span className="font-semibold text-emerald-900">
                    Hasil Prediksi AI: {aiPrediction.category}
                  </span>
                  <p className="text-[11px] text-emerald-700">Kategori telah dipilih secara otomatis</p>
                </div>
              </div>
              <span className="font-mono text-xs font-bold text-emerald-800 bg-white px-2 py-0.5 rounded-md border border-emerald-200">
                {formatPercentage(aiPrediction.confidence)}
              </span>
            </div>
          ) : null}

          {/* Title Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Judul Laporan <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Contoh: Tumpukan botol plastik di pinggir jalan"
              className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-xs sm:text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all"
            />
          </div>

          {/* Category Dropdown */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Kategori Sampah
            </label>
            <select
              value={selectedCategoryId}
              onChange={(e) =>
                setSelectedCategoryId(e.target.value ? Number(e.target.value) : '')
              }
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs sm:text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all"
            >
              <option value="">-- Pilih Kategori (Opsional / AI Terpilih) --</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* GPS Coordinates */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-700">
                Koordinat Lokasi GPS <span className="text-rose-500">*</span>
              </label>
              <button
                type="button"
                onClick={handleGetCurrentLocation}
                disabled={isLocating}
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 hover:text-emerald-700 transition-colors"
              >
                <Navigation className={cn('h-3 w-3', isLocating && 'animate-spin')} />
                <span>{isLocating ? 'Mendeteksi...' : 'Gunakan GPS Saat Ini'}</span>
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2.5">
              <input
                type="text"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                placeholder="Latitude"
                className="rounded-xl border border-slate-300 px-3 py-2 text-xs font-mono text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
              <input
                type="text"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                placeholder="Longitude"
                className="rounded-xl border border-slate-300 px-3 py-2 text-xs font-mono text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>
          </div>

          {/* Address Note & Description */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Patokan Alamat (Opsional)
            </label>
            <input
              type="text"
              value={addressNote}
              onChange={(e) => setAddressNote(e.target.value)}
              placeholder="Contoh: Dekat Pos Ronda RT 04 / Sebelah Minimarket"
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-xs sm:text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Deskripsi Tambahan (Opsional)
            </label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Jelaskan kondisi tumpukan sampah atau tingkat keparahannya..."
              className="w-full rounded-xl border border-slate-300 px-3 py-1.5 text-xs sm:text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 resize-none"
            />
          </div>

          {/* Footer Submit Button */}
          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !title.trim() || !selectedFile}
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2 text-xs font-semibold text-white shadow-xs hover:bg-emerald-700 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isSubmitting && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              <span>Kirim Laporan Sampah</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
