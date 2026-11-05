'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  X,
  Upload,
  Camera,
  MapPin,
  Sparkles,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Navigation,
  Send,
  RefreshCw,
  Info,
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
  const [latitude, setLatitude] = useState<string>('-6.208800');
  const [longitude, setLongitude] = useState<string>('106.845600');
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | ''>('');

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // AI inference state
  const [isPredicting, setIsPredicting] = useState(false);
  const [aiPrediction, setAiPrediction] = useState<PredictResponseData | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  // Form submission state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [isLocating, setIsLocating] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Set default category when categories load or modal opens
  useEffect(() => {
    if (categories.length > 0 && selectedCategoryId === '') {
      setSelectedCategoryId(categories[0].id);
    }
  }, [categories, selectedCategoryId]);

  if (!isOpen) return null;

  const handleSelectCategory = (catId: number) => {
    setSelectedCategoryId(catId);
    const cat = categories.find((c) => c.id === catId);
    if (cat && cat.name && (!title.trim() || title.startsWith('Tumpukan Sampah'))) {
      setTitle(`Tumpukan Sampah ${cat.name}`);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    setAiPrediction(null);
    setAiError(null);
    setFormError(null);

    // Automatically trigger AI classification (MobileNetV2)
    setIsPredicting(true);
    try {
      const res = await predictApi.predict(file);
      setAiPrediction(res.data);

      // Auto-match category from AI prediction
      const predictedCategory = (res.data.category || '').toLowerCase();
      const matched = categories.find(
        (c) =>
          (c?.name && (
            c.name.toLowerCase().includes(predictedCategory) ||
            predictedCategory.includes(c.name.toLowerCase())
          )) ||
          (c?.slug && predictedCategory.includes(c.slug.toLowerCase()))
      );

      if (matched && matched.name) {
        setSelectedCategoryId(matched.id);
        if (!title.trim() || title.startsWith('Tumpukan Sampah')) {
          setTitle(`Tumpukan Sampah ${matched.name}`);
        }
      } else {
        if (!title.trim() || title.startsWith('Tumpukan Sampah')) {
          setTitle(`Tumpukan Sampah ${res.data.category || 'Baru'}`);
        }
      }
    } catch (err: unknown) {
      console.warn('AI preview unavailable:', err);
      setAiError('AI tidak dapat memproses gambar saat ini. Anda dapat memilih kategori secara manual.');
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
    setFormError(null);
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
        setFormError('Gagal mendapatkan lokasi GPS. Pastikan izin lokasi aktif pada peramban Anda.');
        setIsLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!selectedFile) {
      setFormError('Harap ambil atau unggah foto bukti sampah terlebih dahulu.');
      return;
    }

    if (!title.trim()) {
      setFormError('Judul laporan wajib diisi.');
      return;
    }

    const latNum = parseFloat(latitude);
    const lngNum = parseFloat(longitude);
    if (isNaN(latNum) || isNaN(lngNum)) {
      setFormError('Koordinat GPS tidak valid.');
      return;
    }

    // Fallback category id if somehow not set
    const finalCatId =
      selectedCategoryId !== ''
        ? selectedCategoryId
        : categories.length > 0
        ? categories[0].id
        : 1;

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('title', title.trim());
      formData.append('category_id', finalCatId.toString());
      formData.append('latitude', latNum.toString());
      formData.append('longitude', lngNum.toString());
      if (description.trim()) {
        formData.append('description', description.trim());
      }
      if (addressNote.trim()) {
        formData.append('address_note', addressNote.trim());
      }
      // CRITICAL: FastAPI contract requires field name 'file'
      formData.append('file', selectedFile);

      await reportsApi.createReport(formData);

      // Successfully submitted
      onReportCreated();
      onClose();
    } catch (err: unknown) {
      let errorMsg = 'Gagal mengirimkan laporan sampah. Periksa koneksi backend Anda.';
      const resData = (err as { response?: { data?: { detail?: unknown } } })?.response?.data;
      if (resData?.detail) {
        if (typeof resData.detail === 'string') {
          errorMsg = resData.detail;
        } else if (Array.isArray(resData.detail)) {
          errorMsg = resData.detail
            .map((item: { msg?: string; loc?: string[] }) => item.msg || JSON.stringify(item))
            .join(', ');
        } else if (typeof resData.detail === 'object') {
          errorMsg = JSON.stringify(resData.detail);
        }
      }
      setFormError(errorMsg);
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
      <div className="relative w-full max-w-xl bg-white rounded-t-3xl sm:rounded-2xl shadow-2xl border-t sm:border border-slate-200 overflow-hidden max-h-[92vh] sm:max-h-[90vh] flex flex-col animate-in slide-in-from-bottom duration-300 sm:zoom-in-95 sm:duration-150 sm:my-6">
        {/* Mobile Bottom Sheet Tactile Drag Handle */}
        <div className="w-full pt-3 pb-1.5 flex justify-center sm:hidden bg-slate-50/70 cursor-grab">
          <div className="w-12 h-1.5 rounded-full bg-slate-300" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 sm:px-6 bg-slate-50/70">
          <div>
            <h2 className="font-sans text-lg font-bold text-slate-900">
              Form Laporan Sampah
            </h2>
            <p className="font-sans text-xs text-slate-500">
              Klasifikasi otomatis AI MobileNetV2 &amp; Geotagging GPS presisi
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-200/60 hover:text-slate-700 transition-colors"
            aria-label="Tutup form"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Form Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-4">
          {formError && (
            <div className="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-xs text-rose-800">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600 mt-0.5" />
              <div className="flex-1 font-medium leading-relaxed">{formError}</div>
            </div>
          )}

          {/* 1. Photo Capture Section (Dashed Border when empty, filled preview when loaded) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
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
              <div className="relative w-full h-52 sm:h-56 rounded-2xl overflow-hidden border border-slate-200 bg-slate-900 flex items-center justify-center group shadow-xs">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={previewUrl} alt="Preview Bukti Sampah" className="w-full h-full object-cover" />
                <div className="absolute top-3 right-3">
                  <span className="inline-flex items-center gap-1.5 bg-black/70 backdrop-blur-md text-emerald-400 text-xs font-semibold px-2.5 py-1 rounded-lg border border-white/10">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>Foto Terpilih</span>
                  </span>
                </div>
                <div className="absolute inset-0 bg-slate-950/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="inline-flex items-center gap-2 bg-white text-slate-900 text-xs font-bold px-4 py-2 rounded-xl shadow-lg hover:bg-slate-100 transition-transform active:scale-95"
                  >
                    <Upload className="h-4 w-4 text-emerald-600" />
                    <span>Ganti Foto</span>
                  </button>
                </div>
              </div>
            ) : (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="w-full rounded-2xl border-2 border-dashed border-emerald-300 hover:border-emerald-500 bg-emerald-50/40 hover:bg-emerald-50/70 transition-all cursor-pointer flex flex-col items-center justify-center py-8 px-4 text-center group"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700 group-hover:scale-110 transition-transform mb-3 shadow-xs">
                  <Camera className="h-6 w-6" />
                </div>
                <p className="text-sm font-bold text-slate-900">Ambil Foto Bukti Sampah</p>
                <p className="text-xs text-slate-500 mt-1 max-w-sm">
                  AI MobileNetV2 akan mendeteksi otomatis kategori sampah perkotaan
                </p>
                <div className="mt-4 flex items-center gap-2">
                  <span className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-3.5 py-1.5 text-xs font-bold text-white shadow-xs group-hover:bg-emerald-700">
                    <Upload className="h-3.5 w-3.5" />
                    <span>Pilih Foto dari Galeri / Kamera</span>
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* 2. AI Detection Banner (Progress bar + confidence badge + 1-Tap quick chips) */}
          {isPredicting && (
            <div className="flex items-center gap-3 p-4 rounded-2xl bg-emerald-50/90 border border-emerald-200 text-xs text-emerald-900 animate-pulse">
              <Loader2 className="h-5 w-5 animate-spin text-emerald-600 shrink-0" />
              <div>
                <p className="font-bold text-emerald-950">AI MobileNetV2 Memindai...</p>
                <p className="text-[11px] text-emerald-700">Mengklasifikasikan jenis sampah secara real-time</p>
              </div>
            </div>
          )}

          {aiError && (
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800">
              <Info className="h-4 w-4 shrink-0 text-amber-600" />
              <p>{aiError}</p>
            </div>
          )}

          {aiPrediction && !isPredicting && (
            <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200/90 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-xs">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-emerald-950">
                      Deteksi AI MobileNetV2
                    </span>
                    <p className="text-[11px] text-emerald-700">Kategori terdeteksi otomatis</p>
                  </div>
                </div>
                <span className="font-mono text-xs font-extrabold text-emerald-800 bg-white px-2.5 py-1 rounded-lg border border-emerald-200 shadow-2xs">
                  {formatPercentage(aiPrediction.confidence)}
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-white/80 rounded-full h-2 overflow-hidden border border-emerald-100">
                <div
                  className="bg-emerald-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.round(aiPrediction.confidence * 100))}%` }}
                />
              </div>

              {/* 1-Tap Category Quick Chips (Mirrors Mobile UX) */}
              <div className="pt-1">
                <p className="text-[11px] font-bold text-slate-700 mb-1.5 flex items-center gap-1">
                  <span>Koreksi Kategori (1-Ketuk jika AI meleset):</span>
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {categories.map((cat) => {
                    const isSelected = selectedCategoryId === cat.id;
                    return (
                      <button
                        type="button"
                        key={cat.id}
                        onClick={() => handleSelectCategory(cat.id)}
                        className={cn(
                          'inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all',
                          isSelected
                            ? 'bg-emerald-600 text-white shadow-xs'
                            : 'bg-white text-slate-700 border border-slate-200 hover:border-emerald-400'
                        )}
                      >
                        {isSelected && <CheckCircle2 className="h-3 w-3" />}
                        <span>{cat?.name || 'Kategori'}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* 3. Geotagging Lokasi GPS Card */}
          <div className="p-4 rounded-2xl border border-slate-200/90 bg-slate-50/70 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-50 text-blue-600 border border-blue-200">
                  <MapPin className="h-4 w-4" />
                </div>
                <div>
                  <span className="text-xs font-bold text-slate-900">Geotagging Lokasi GPS</span>
                  <p className="text-[11px] text-slate-500">Koordinat bukti pelaporan lapangan</p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleGetCurrentLocation}
                disabled={isLocating}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 active:scale-95 transition-all shadow-2xs"
              >
                <Navigation className={cn('h-3.5 w-3.5 text-emerald-600', isLocating && 'animate-spin')} />
                <span>{isLocating ? 'Mendeteksi...' : 'GPS Saya'}</span>
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="bg-white rounded-xl border border-slate-200 px-3 py-1.5 flex items-center justify-between">
                <span className="text-slate-400 text-[10px]">LAT</span>
                <span className="font-semibold text-slate-800">{latitude}</span>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 px-3 py-1.5 flex items-center justify-between">
                <span className="text-slate-400 text-[10px]">LNG</span>
                <span className="font-semibold text-slate-800">{longitude}</span>
              </div>
            </div>
          </div>

          {/* 4. Form Fields */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
              Judul Laporan <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Contoh: Tumpukan Botol Plastik di Pinggir Jalan"
              className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-xs sm:text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all font-sans"
            />
          </div>

          {/* Category Dropdown */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
              Kategori Sampah <span className="text-rose-500">*</span>
            </label>
            <select
              value={selectedCategoryId}
              onChange={(e) => handleSelectCategory(Number(e.target.value))}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-xs sm:text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all font-sans"
            >
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c?.name || 'Kategori'}
                </option>
              ))}
            </select>
          </div>

          {/* Address Note & Description */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
              Patokan Alamat (Opsional)
            </label>
            <input
              type="text"
              value={addressNote}
              onChange={(e) => setAddressNote(e.target.value)}
              placeholder="Contoh: Dekat Pos Ronda RT 04 / Sebelah Minimarket"
              className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-xs sm:text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
              Deskripsi Tambahan (Opsional)
            </label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Jelaskan kondisi tumpukan sampah atau perkiraan volumenya..."
              className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-xs sm:text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 resize-none font-sans"
            />
          </div>

          {/* 5. Sticky Bottom Submit Action */}
          <div className="pt-3 border-t border-slate-200/80 flex flex-col sm:flex-row items-center justify-end gap-2.5 sticky bottom-0 bg-white/95 pb-2 backdrop-blur-xs">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="w-full sm:w-auto rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs order-2 sm:order-1"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !selectedFile || !title.trim()}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-6 py-2.5 text-xs sm:text-sm font-bold text-white shadow-sm hover:bg-emerald-700 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition-all order-1 sm:order-2 min-h-[44px]"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Mengirim Laporan...</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  <span>Kirim Laporan Sampah</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
