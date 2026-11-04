'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import type { CategoryDistributionItem } from '@/types/api';

export type CategoryDistribution = CategoryDistributionItem;

export interface CategoryChartProps {
  distribution: CategoryDistribution[];
  totalReports: number;
  isLoading?: boolean;
  className?: string;
}

interface CategoryStyleConfig {
  name: string;
  hex: string;
  cardBg: string;
  cardBorder: string;
  textClass: string;
  badgeBg: string;
  badgeText: string;
  barColor: string;
}

const CANONICAL_CATEGORIES: Record<string, CategoryStyleConfig> = {
  'Organic Waste': {
    name: 'Organic Waste',
    hex: '#10b981',
    cardBg: 'bg-emerald-50/60 hover:bg-emerald-50/90',
    cardBorder: 'border-emerald-200/90',
    textClass: 'text-emerald-900',
    badgeBg: 'bg-emerald-100',
    badgeText: 'text-emerald-800',
    barColor: 'bg-emerald-500',
  },
  'Plastic Waste': {
    name: 'Plastic Waste',
    hex: '#0284c7',
    cardBg: 'bg-sky-50/60 hover:bg-sky-50/90',
    cardBorder: 'border-sky-200/90',
    textClass: 'text-sky-900',
    badgeBg: 'bg-sky-100',
    badgeText: 'text-sky-800',
    barColor: 'bg-sky-500',
  },
  'Paper Waste': {
    name: 'Paper Waste',
    hex: '#f59e0b',
    cardBg: 'bg-amber-50/60 hover:bg-amber-50/90',
    cardBorder: 'border-amber-200/90',
    textClass: 'text-amber-900',
    badgeBg: 'bg-amber-100',
    badgeText: 'text-amber-800',
    barColor: 'bg-amber-500',
  },
};

export default function CategoryChart({
  distribution = [],
  totalReports = 0,
  isLoading = false,
  className,
}: CategoryChartProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          'rounded-3xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-sm animate-pulse',
          className
        )}
        data-testid="category-chart-skeleton"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="h-5 w-48 rounded bg-slate-200" />
          <div className="h-4 w-24 rounded bg-slate-200" />
        </div>
        <div className="h-4 w-full rounded-full bg-slate-200 mb-6" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="rounded-2xl border border-slate-200 p-5 space-y-3">
              <div className="h-4 w-24 rounded bg-slate-200" />
              <div className="h-7 w-16 rounded bg-slate-200" />
              <div className="h-2 w-full rounded bg-slate-100" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const targetCategoryNames = ['Organic Waste', 'Plastic Waste', 'Paper Waste'];

  const normalizedItems = targetCategoryNames.map((name) => {
    const found = distribution.find(
      (d) => d.category?.trim().toLowerCase() === name.toLowerCase()
    );
    const count = found ? found.count : 0;
    let percentage = 0;
    if (totalReports > 0) {
      percentage = found && typeof found.percentage === 'number'
        ? found.percentage
        : (count / totalReports) * 100;
    }
    const config = CANONICAL_CATEGORIES[name];
    return {
      name,
      count,
      percentage: Math.max(0, percentage),
      config,
    };
  });

  let cumulativeX = 0;
  const segments = normalizedItems.map((item) => {
    const width = totalReports > 0 ? item.percentage : 0;
    const x = cumulativeX;
    cumulativeX += width;
    return {
      ...item,
      x,
      width,
    };
  });

  return (
    <div
      className={cn(
        'rounded-3xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-sm transition-all',
        className
      )}
      data-testid="category-chart"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <div>
          <h3 className="font-sans text-xl font-extrabold text-slate-900 tracking-tight">
            Distribusi Kategori Sampah
          </h3>
          <p className="font-sans text-xs sm:text-sm text-slate-500 mt-0.5">
            Proporsi laporan sampah berdasarkan hasil inferensi AI MobileNetV2 presisi tinggi
          </p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <span className="font-sans text-xs text-slate-500 font-medium">Total Terklasifikasi:</span>
          <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
            {totalReports} Laporan
          </span>
        </div>
      </div>

      {/* Proportional Segmented Progress Bar */}
      <div className="relative mb-6">
        <div className="h-4 w-full rounded-full bg-slate-100 border border-slate-200/80 overflow-hidden flex shadow-inner">
          {totalReports > 0 ? (
            segments.map((item) => {
              if (item.width <= 0) return null;
              return (
                <div
                  key={item.name}
                  style={{ width: `${item.width}%`, backgroundColor: item.config.hex }}
                  className="h-full transition-all duration-500 first:rounded-l-full last:rounded-r-full"
                  title={`${item.name}: ${item.count} laporan (${item.percentage.toFixed(1)}%)`}
                />
              );
            })
          ) : (
            <div className="w-full h-full bg-slate-200/60" />
          )}
        </div>

        {totalReports === 0 && (
          <p className="mt-2 text-center text-xs text-slate-400 font-medium">
            Belum ada data laporan sampah untuk visualisasi proporsi.
          </p>
        )}
      </div>

      {/* Modern High-Contrast Category Cards Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {normalizedItems.map((item) => {
          const formattedPct = totalReports > 0 ? `${item.percentage.toFixed(1)}%` : '0%';
          return (
            <div
              key={item.name}
              className={cn(
                'group relative rounded-2xl border p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md',
                item.config.cardBorder,
                item.config.cardBg
              )}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span
                    className="h-3 w-3 rounded-full shrink-0 shadow-xs ring-2 ring-white"
                    style={{ backgroundColor: item.config.hex }}
                    aria-hidden="true"
                  />
                  <span className={cn('font-sans text-xs font-bold tracking-tight', item.config.textClass)}>
                    {item.name}
                  </span>
                </div>
                <span
                  className={cn(
                    'font-mono text-xs px-2.5 py-0.5 rounded-full font-bold',
                    item.config.badgeBg,
                    item.config.badgeText
                  )}
                >
                  {item.count}
                </span>
              </div>

              <div className="mt-4 flex items-baseline justify-between">
                <span className="font-sans text-3xl font-black tracking-tight text-slate-900">
                  {formattedPct}
                </span>
                <span className="font-sans text-xs font-medium text-slate-500">
                  {item.count} dari {totalReports}
                </span>
              </div>

              {/* Progress Line */}
              <div className="mt-3.5 h-2 w-full rounded-full bg-white/80 overflow-hidden border border-slate-200/60">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(100, Math.max(0, item.percentage))}%`,
                    backgroundColor: item.config.hex,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
