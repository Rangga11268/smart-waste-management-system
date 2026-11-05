'use client';

import React, { useState } from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import { PieChart, BarChart3, Layers, CheckCircle2, Clock, Truck, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { CategoryDistributionItem } from '@/types/api';

// Register Chart.js plugins and controllers
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
);

export interface StatusSummary {
  pending: number;
  inProgress: number;
  completed: number;
  rejected: number;
}

export interface CategoryChartProps {
  distribution: CategoryDistributionItem[];
  totalReports: number;
  statusSummary?: StatusSummary;
  isLoading?: boolean;
  className?: string;
}

export default function CategoryChart({
  distribution = [],
  totalReports = 0,
  statusSummary = { pending: 0, inProgress: 0, completed: 0, rejected: 0 },
  isLoading = false,
  className,
}: CategoryChartProps) {
  const [activeTab, setActiveTab] = useState<'both' | 'category' | 'status'>('both');

  if (isLoading) {
    return (
      <div
        className={cn(
          'rounded-3xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-sm animate-pulse space-y-6',
          className
        )}
      >
        <div className="flex items-center justify-between">
          <div className="h-6 w-48 rounded-lg bg-slate-200" />
          <div className="h-8 w-36 rounded-xl bg-slate-200" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-64 rounded-2xl bg-slate-100" />
          <div className="h-64 rounded-2xl bg-slate-100" />
        </div>
      </div>
    );
  }

  // 1. Prepare Category Doughnut Data
  const categoriesCanonical = [
    { key: 'organic', label: 'Organic Waste', color: '#10b981', hoverColor: '#059669' },
    { key: 'plastic', label: 'Plastic Waste', color: '#0284c7', hoverColor: '#0369a1' },
    { key: 'paper', label: 'Paper Waste', color: '#f59e0b', hoverColor: '#d97706' },
  ];

  const categoryCounts = categoriesCanonical.map((cat) => {
    const found = distribution.find(
      (d) => d.category?.trim().toLowerCase() === cat.label.toLowerCase()
    );
    return found ? found.count : 0;
  });

  const doughnutData = {
    labels: categoriesCanonical.map((c) => c.label),
    datasets: [
      {
        data: categoryCounts.every((c) => c === 0) ? [1, 1, 1] : categoryCounts,
        backgroundColor: categoriesCanonical.map((c) => c.color),
        hoverBackgroundColor: categoriesCanonical.map((c) => c.hoverColor),
        borderColor: '#ffffff',
        borderWidth: 3,
        hoverOffset: 6,
      },
    ],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '72%',
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleFont: { size: 12, weight: 'bold' as const, family: 'Inter, sans-serif' },
        bodyFont: { size: 12, family: 'Inter, sans-serif' },
        padding: 10,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: (context: any) => {
            const label = context.label || '';
            const val = context.raw || 0;
            const pct = totalReports > 0 ? ((val / totalReports) * 100).toFixed(1) : '0.0';
            return ` ${label}: ${val} laporan (${pct}%)`;
          },
        },
      },
    },
  };

  // 2. Prepare Status Bar Chart Data
  const statusesCanonical = [
    { label: 'Menunggu', key: 'pending', value: statusSummary.pending, color: '#a855f7' },
    { label: 'Ditangani', key: 'inProgress', value: statusSummary.inProgress, color: '#3b82f6' },
    { label: 'Selesai', key: 'completed', value: statusSummary.completed, color: '#10b981' },
    { label: 'Ditolak', key: 'rejected', value: statusSummary.rejected, color: '#f43f5e' },
  ];

  const barData = {
    labels: statusesCanonical.map((s) => s.label),
    datasets: [
      {
        label: 'Jumlah Laporan',
        data: statusesCanonical.map((s) => s.value),
        backgroundColor: statusesCanonical.map((s) => s.color),
        borderRadius: 8,
        borderSkipped: false,
        maxBarThickness: 36,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleFont: { size: 12, weight: 'bold' as const, family: 'Inter, sans-serif' },
        bodyFont: { size: 12, family: 'Inter, sans-serif' },
        padding: 10,
        cornerRadius: 8,
        callbacks: {
          label: (context: any) => ` ${context.parsed.y} berkas laporan`,
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: { size: 11, family: 'Inter, sans-serif', weight: 'bold' as const },
          color: '#64748b',
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: '#f1f5f9',
        },
        ticks: {
          stepSize: 1,
          font: { size: 11, family: 'Inter, sans-serif' },
          color: '#94a3b8',
        },
      },
    },
  };

  return (
    <div
      className={cn(
        'rounded-3xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-sm transition-all space-y-6',
        className
      )}
    >
      {/* Header with Title and Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-5 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-2xs">
              <PieChart className="h-5 w-5" />
            </div>
            <h3 className="font-sans text-xl font-extrabold text-slate-900 tracking-tight">
              Visualisasi Analitik Operasional
            </h3>
          </div>
          <p className="font-sans text-xs sm:text-sm text-slate-500 mt-1">
            Grafik interaktif Chart.js: proporsi kategori sampah terdeteksi AI dan status progres armada
          </p>
        </div>

        {/* View Switcher Pills */}
        <div className="flex items-center bg-slate-100 p-1 rounded-xl self-start sm:self-auto border border-slate-200/80">
          <button
            type="button"
            onClick={() => setActiveTab('both')}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs font-bold transition-all',
              activeTab === 'both'
                ? 'bg-white text-slate-900 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            Kedua Grafik
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('category')}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs font-bold transition-all',
              activeTab === 'category'
                ? 'bg-white text-slate-900 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            Kategori
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('status')}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs font-bold transition-all',
              activeTab === 'status'
                ? 'bg-white text-slate-900 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            Status
          </button>
        </div>
      </div>

      {/* Main Charts Area */}
      <div
        className={cn(
          'grid gap-6 items-stretch',
          activeTab === 'both' ? 'grid-cols-1 lg:grid-cols-12' : 'grid-cols-1'
        )}
      >
        {/* Chart 1: Doughnut Kategori Sampah */}
        {(activeTab === 'both' || activeTab === 'category') && (
          <div
            className={cn(
              'rounded-2xl border border-slate-200/90 bg-slate-50/40 p-5 flex flex-col justify-between space-y-4',
              activeTab === 'both' ? 'lg:col-span-5' : 'w-full'
            )}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Proporsi Kategori Sampah
              </span>
              <span className="font-mono text-xs font-semibold text-slate-500 bg-white px-2 py-0.5 rounded-md border border-slate-200 shadow-2xs">
                Total: {totalReports}
              </span>
            </div>

            {/* Canvas Container */}
            <div className="relative h-56 w-full flex items-center justify-center">
              <Doughnut data={doughnutData} options={doughnutOptions} />
              {/* Center Metric */}
              <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="font-sans text-2xl font-black text-slate-900 leading-none">
                  {totalReports}
                </span>
                <span className="text-[10px] uppercase font-bold text-slate-400 mt-1">
                  Laporan
                </span>
              </div>
            </div>

            {/* Custom Interactive Legend Badges */}
            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-200/80">
              {categoriesCanonical.map((cat, idx) => {
                const count = categoryCounts[idx];
                const pct = totalReports > 0 ? Math.round((count / totalReports) * 100) : 0;
                return (
                  <div
                    key={cat.key}
                    className="p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs flex flex-col"
                  >
                    <div className="flex items-center gap-1.5 mb-1">
                      <span
                        className="h-2.5 w-2.5 rounded-full shrink-0"
                        style={{ backgroundColor: cat.color }}
                      />
                      <span className="text-[10px] font-bold text-slate-700 truncate">
                        {cat.label.replace(' Waste', '')}
                      </span>
                    </div>
                    <span className="font-mono text-sm font-extrabold text-slate-900">
                      {count} <span className="text-[10px] font-medium text-slate-400">({pct}%)</span>
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Chart 2: Bar Chart Status Penanganan */}
        {(activeTab === 'both' || activeTab === 'status') && (
          <div
            className={cn(
              'rounded-2xl border border-slate-200/90 bg-slate-50/40 p-5 flex flex-col justify-between space-y-4',
              activeTab === 'both' ? 'lg:col-span-7' : 'w-full'
            )}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-slate-600" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Status Triage &amp; Penanganan Armada
                </span>
              </div>
              <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                State Machine Live
              </span>
            </div>

            {/* Canvas Container */}
            <div className="relative h-56 w-full">
              <Bar data={barData} options={barOptions} />
            </div>

            {/* Bottom Mini Metric Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-200/80">
              {statusesCanonical.map((st) => (
                <div
                  key={st.key}
                  className="p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs flex items-center justify-between"
                >
                  <div className="flex items-center gap-1.5">
                    <span
                      className="h-2 w-2 rounded-full shrink-0"
                      style={{ backgroundColor: st.color }}
                    />
                    <span className="text-[11px] font-semibold text-slate-600">{st.label}</span>
                  </div>
                  <span className="font-mono text-xs font-bold text-slate-900">{st.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
