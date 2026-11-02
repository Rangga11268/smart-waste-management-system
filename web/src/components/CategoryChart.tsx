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
  bgLight: string;
  textClass: string;
  borderClass: string;
  badgeBg: string;
  badgeText: string;
  dotColor: string;
}

const CANONICAL_CATEGORIES: Record<string, CategoryStyleConfig> = {
  'Organic Waste': {
    name: 'Organic Waste',
    hex: '#16a34a',
    bgLight: 'bg-green-50',
    textClass: 'text-green-800',
    borderClass: 'border-green-200',
    badgeBg: 'bg-green-100',
    badgeText: 'text-green-800',
    dotColor: '#16a34a',
  },
  'Plastic Waste': {
    name: 'Plastic Waste',
    hex: '#0284c7',
    bgLight: 'bg-sky-50',
    textClass: 'text-sky-800',
    borderClass: 'border-sky-200',
    badgeBg: 'bg-sky-100',
    badgeText: 'text-sky-800',
    dotColor: '#0284c7',
  },
  'Paper Waste': {
    name: 'Paper Waste',
    hex: '#d97706',
    bgLight: 'bg-amber-50',
    textClass: 'text-amber-800',
    borderClass: 'border-amber-200',
    badgeBg: 'bg-amber-100',
    badgeText: 'text-amber-800',
    dotColor: '#d97706',
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
          'rounded-xl border border-slate-200 bg-white p-6 shadow-sm animate-pulse',
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
            <div key={i} className="rounded-xl border border-slate-200 p-4 space-y-2">
              <div className="h-4 w-24 rounded bg-slate-200" />
              <div className="h-6 w-16 rounded bg-slate-200" />
              <div className="h-3 w-full rounded bg-slate-100" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Canonical ordering for the 3 main waste categories
  const targetCategoryNames = ['Organic Waste', 'Plastic Waste', 'Paper Waste'];

  // Normalize distribution data
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

  // Calculate cumulative X coordinates for SVG segmented meter
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
        'rounded-xl border border-slate-200 bg-white p-6 shadow-sm',
        className
      )}
      data-testid="category-chart"
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
        <div>
          <h3 className="font-heading text-lg font-bold text-slate-900">
            Distribusi Kategori Sampah
          </h3>
          <p className="font-sans text-xs text-slate-500">
            Proporsi laporan sampah berdasarkan hasil inferensi AI MobileNetV2
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-sans text-xs text-slate-500">Total Terklasifikasi:</span>
          <span className="font-mono text-xs font-semibold text-slate-900 bg-slate-100 px-2 py-0.5 rounded-md border border-slate-200">
            {totalReports} Laporan
          </span>
        </div>
      </div>

      {/* Segmented Proportional Meter (SVG + CSS) */}
      <div className="relative mb-6">
        <svg
          className="w-full h-4 rounded-full overflow-hidden bg-slate-100 border border-slate-200 shadow-inner"
          viewBox="0 0 100 12"
          preserveAspectRatio="none"
          aria-label="Grafik proporsi kategori sampah"
          role="img"
        >
          {totalReports > 0 ? (
            segments.map((item) => {
              if (item.width <= 0) return null;
              return (
                <rect
                  key={item.name}
                  x={`${item.x}%`}
                  y="0"
                  width={`${item.width}%`}
                  height="12"
                  fill={item.config.hex}
                >
                  <title>{`${item.name}: ${item.count} laporan (${item.percentage.toFixed(1)}%)`}</title>
                </rect>
              );
            })
          ) : (
            <rect x="0" y="0" width="100%" height="12" fill="#e2e8f0" />
          )}
        </svg>

        {totalReports === 0 && (
          <p className="mt-2 text-center text-xs text-slate-400">
            Belum ada data laporan sampah untuk visualisasi proporsi.
          </p>
        )}
      </div>

      {/* Category Metric Cards Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {normalizedItems.map((item) => {
          const formattedPct = totalReports > 0 ? `${item.percentage.toFixed(1)}%` : '0%';
          return (
            <div
              key={item.name}
              className={cn(
                'group relative rounded-xl border p-4 transition-all hover:shadow-xs',
                item.config.borderClass,
                item.config.bgLight
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span
                    className="h-2.5 w-2.5 rounded-full shrink-0 shadow-xs"
                    style={{ backgroundColor: item.config.hex }}
                    aria-hidden="true"
                  />
                  <span className={cn('font-sans text-xs font-semibold', item.config.textClass)}>
                    {item.name}
                  </span>
                </div>
                <span
                  className={cn(
                    'font-mono text-xs px-2 py-0.5 rounded-full font-medium',
                    item.config.badgeBg,
                    item.config.badgeText
                  )}
                >
                  {item.count}
                </span>
              </div>

              <div className="mt-3 flex items-baseline justify-between">
                <span className="font-heading text-2xl font-bold tracking-tight text-slate-900">
                  {formattedPct}
                </span>
                <span className="font-sans text-xs text-slate-500">
                  {item.count} dari {totalReports}
                </span>
              </div>

              {/* Mini individual bar */}
              <div className="mt-2.5 h-1.5 w-full rounded-full bg-white/70 overflow-hidden border border-slate-200/50">
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
