import React from 'react';
import { LucideIcon, MoreHorizontal } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface StatCardTrend {
  value: string;
  isPositive?: boolean;
}

export interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon | React.ElementType;
  trend?: StatCardTrend;
  variant?: 'black' | 'purple' | 'blue' | 'emerald' | 'default';
  isLoading?: boolean;
  className?: string;
}

/* Unified, high-contrast Eco-Tech palette: Slate 900 anchor with crisp executive cards */
const cardStyles = {
  black: {
    bg: 'bg-[#0f172a] border-slate-800 text-white shadow-lg shadow-slate-950/20',
    title: 'text-slate-300 font-semibold text-sm',
    value: 'text-white',
    pill: 'bg-white/10 text-white font-semibold border border-white/10',
    subtitle: 'text-slate-300 text-xs',
    dots: 'text-slate-400 hover:text-white',
  },
  purple: {
    bg: 'bg-white border-slate-200/90 text-slate-900 shadow-xs hover:border-slate-300',
    title: 'text-slate-600 font-semibold text-sm',
    value: 'text-slate-900',
    pill: 'bg-amber-50 text-amber-800 font-semibold border border-amber-200/80',
    subtitle: 'text-slate-500 text-xs',
    dots: 'text-slate-400 hover:text-slate-600',
  },
  blue: {
    bg: 'bg-white border-slate-200/90 text-slate-900 shadow-xs hover:border-slate-300',
    title: 'text-slate-600 font-semibold text-sm',
    value: 'text-slate-900',
    pill: 'bg-slate-100 text-slate-800 font-semibold border border-slate-200',
    subtitle: 'text-slate-500 text-xs',
    dots: 'text-slate-400 hover:text-slate-600',
  },
  emerald: {
    bg: 'bg-white border-slate-200/90 text-slate-900 shadow-xs hover:border-slate-300',
    title: 'text-slate-600 font-semibold text-sm',
    value: 'text-slate-900',
    pill: 'bg-emerald-50 text-emerald-800 font-semibold border border-emerald-200/80',
    subtitle: 'text-slate-500 text-xs',
    dots: 'text-slate-400 hover:text-slate-600',
  },
  default: {
    bg: 'bg-white border-slate-200/90 text-slate-900 shadow-xs hover:border-slate-300',
    title: 'text-slate-600 font-semibold text-sm',
    value: 'text-slate-900',
    pill: 'bg-slate-100 text-slate-700 border border-slate-200',
    subtitle: 'text-slate-500 text-xs',
    dots: 'text-slate-400 hover:text-slate-600',
  },
};

export default function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  variant = 'black',
  isLoading = false,
  className,
}: StatCardProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          'rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm animate-pulse',
          className
        )}
        data-testid="stat-card-skeleton"
      >
        <div className="flex items-start justify-between">
          <div className="h-4 w-28 rounded bg-slate-200" />
          <div className="h-4 w-6 rounded bg-slate-200" />
        </div>
        <div className="mt-5 space-y-3">
          <div className="h-10 w-24 rounded bg-slate-200" />
          <div className="h-5 w-28 rounded-md bg-slate-200" />
        </div>
        <div className="mt-5 pt-3 border-t border-slate-100">
          <div className="h-3 w-36 rounded bg-slate-100" />
        </div>
      </div>
    );
  }

  const Icon = icon;
  const style = cardStyles[variant] || cardStyles.black;

  return (
    <div
      className={cn(
        'group relative flex flex-col justify-between rounded-2xl border p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-xl',
        style.bg,
        className
      )}
      data-testid="stat-card"
    >
      {/* Top Header: Title & Action/Icon */}
      <div className="flex items-center justify-between">
        <span className={cn('tracking-wide', style.title)}>
          {title}
        </span>
        <div className="flex items-center gap-1.5">
          {Icon ? (
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-white/10 backdrop-blur-xs">
              <Icon className="h-4 w-4" />
            </div>
          ) : (
            <button
              type="button"
              className={cn('rounded-lg p-1.5 transition-colors min-h-[32px] min-w-[32px] flex items-center justify-center', style.dots)}
              aria-label="Opsi metrik"
            >
              <MoreHorizontal className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Main Metric Value & Trend Badge (Side by Side like reference image) */}
      <div className="mt-4 flex items-baseline gap-3 flex-wrap">
        <div className={cn('text-3xl sm:text-4xl font-extrabold tracking-tight leading-none', style.value)}>
          {value}
        </div>
        {trend && (
          <span
            className={cn(
              'inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold',
              style.pill
            )}
          >
            {trend.value}
          </span>
        )}
      </div>

      {/* Footer Comparison Subtitle */}
      {subtitle && (
        <div className="mt-4 text-xs font-medium">
          <span className={cn('line-clamp-1', style.subtitle)}>
            {subtitle}
          </span>
        </div>
      )}
    </div>
  );
}
