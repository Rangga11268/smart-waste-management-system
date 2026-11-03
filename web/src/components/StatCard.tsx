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

const cardStyles = {
  black: {
    bg: 'bg-slate-900 border-slate-800 text-white shadow-lg shadow-slate-900/10',
    title: 'text-slate-300',
    value: 'text-white',
    pill: 'bg-white/15 text-white border border-white/20',
    subtitle: 'text-slate-400',
    dots: 'text-slate-400 hover:text-white',
  },
  purple: {
    bg: 'bg-gradient-to-br from-fuchsia-600 via-purple-600 to-indigo-600 border-purple-500/40 text-white shadow-lg shadow-purple-600/20',
    title: 'text-purple-100',
    value: 'text-white',
    pill: 'bg-white/20 text-white border border-white/30 backdrop-blur-xs',
    subtitle: 'text-purple-100/90',
    dots: 'text-purple-200 hover:text-white',
  },
  blue: {
    bg: 'bg-gradient-to-br from-blue-600 via-blue-600 to-indigo-700 border-blue-500/40 text-white shadow-lg shadow-blue-600/20',
    title: 'text-blue-100',
    value: 'text-white',
    pill: 'bg-white/20 text-white border border-white/30 backdrop-blur-xs',
    subtitle: 'text-blue-100/90',
    dots: 'text-blue-200 hover:text-white',
  },
  emerald: {
    bg: 'bg-gradient-to-br from-emerald-600 via-teal-600 to-teal-800 border-emerald-500/40 text-white shadow-lg shadow-emerald-600/20',
    title: 'text-emerald-100',
    value: 'text-white',
    pill: 'bg-white/20 text-white border border-white/30 backdrop-blur-xs',
    subtitle: 'text-emerald-100/90',
    dots: 'text-emerald-200 hover:text-white',
  },
  default: {
    bg: 'bg-white border-slate-200 text-slate-900 shadow-sm',
    title: 'text-slate-500',
    value: 'text-slate-900',
    pill: 'bg-slate-100 text-slate-700 border border-slate-200',
    subtitle: 'text-slate-500',
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
          'rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm animate-pulse',
          className
        )}
        data-testid="stat-card-skeleton"
      >
        <div className="flex items-start justify-between">
          <div className="h-4 w-28 rounded bg-slate-200" />
          <div className="h-4 w-6 rounded bg-slate-200" />
        </div>
        <div className="mt-6 flex items-baseline gap-3">
          <div className="h-10 w-24 rounded bg-slate-200" />
          <div className="h-6 w-16 rounded-full bg-slate-200" />
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
        'group relative flex flex-col justify-between rounded-3xl border p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-xl',
        style.bg,
        className
      )}
      data-testid="stat-card"
    >
      {/* Top Header: Title & Action/Icon */}
      <div className="flex items-center justify-between">
        <span className={cn('text-sm font-semibold tracking-wide', style.title)}>
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
              className={cn('rounded p-1 transition-colors', style.dots)}
              aria-label="Opsi metrik"
            >
              <MoreHorizontal className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Main Metric Value & Trend Pill */}
      <div className="mt-5 flex items-baseline flex-wrap gap-2.5">
        <div className={cn('text-3xl sm:text-4xl font-extrabold tracking-tight', style.value)}>
          {value}
        </div>
        {trend && (
          <span
            className={cn(
              'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold',
              style.pill
            )}
          >
            {trend.value}
          </span>
        )}
      </div>

      {/* Footer Comparison Subtitle */}
      {subtitle && (
        <div className="mt-5 pt-3 border-t border-white/10 flex items-center justify-between text-xs">
          <span className={cn('font-medium line-clamp-1', style.subtitle)}>
            {subtitle}
          </span>
        </div>
      )}
    </div>
  );
}
