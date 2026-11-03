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

/* Deep, high-contrast, comfortable backgrounds that meet WCAG standards without eye strain */
const cardStyles = {
  black: {
    bg: 'bg-slate-900 border-slate-800 text-white shadow-md shadow-slate-900/10',
    title: 'text-slate-300 font-semibold',
    value: 'text-white',
    pill: 'bg-slate-800 text-slate-200 border border-slate-700',
    subtitle: 'text-slate-300',
    dots: 'text-slate-400 hover:text-white',
  },
  purple: {
    bg: 'bg-[#18112e] border-purple-900/50 text-white shadow-md shadow-purple-950/20',
    title: 'text-purple-200 font-semibold',
    value: 'text-white',
    pill: 'bg-purple-900/60 text-purple-200 border border-purple-700/60',
    subtitle: 'text-purple-200/90',
    dots: 'text-purple-300 hover:text-white',
  },
  blue: {
    bg: 'bg-[#0e1d3d] border-blue-900/50 text-white shadow-md shadow-blue-950/20',
    title: 'text-sky-200 font-semibold',
    value: 'text-white',
    pill: 'bg-blue-900/60 text-sky-200 border border-blue-700/60',
    subtitle: 'text-sky-200/90',
    dots: 'text-sky-300 hover:text-white',
  },
  emerald: {
    bg: 'bg-[#09221b] border-emerald-900/50 text-white shadow-md shadow-emerald-950/20',
    title: 'text-emerald-200 font-semibold',
    value: 'text-white',
    pill: 'bg-emerald-900/60 text-emerald-200 border border-emerald-700/60',
    subtitle: 'text-emerald-200/90',
    dots: 'text-emerald-300 hover:text-white',
  },
  default: {
    bg: 'bg-white border-slate-200 text-slate-900 shadow-sm',
    title: 'text-slate-600 font-semibold',
    value: 'text-slate-900',
    pill: 'bg-slate-100 text-slate-700 border border-slate-200',
    subtitle: 'text-slate-600',
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
        <div className="mt-5 space-y-3">
          <div className="h-10 w-24 rounded bg-slate-200" />
          <div className="h-5 w-28 rounded-full bg-slate-200" />
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
        <span className={cn('text-sm tracking-wide', style.title)}>
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

      {/* Main Metric Value (Uncramped with Dedicated Breathing Room) */}
      <div className="mt-5">
        <div className={cn('text-4xl sm:text-5xl font-black tracking-tight leading-none', style.value)}>
          {value}
        </div>
        {trend && (
          <div className="mt-3">
            <span
              className={cn(
                'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold',
                style.pill
              )}
            >
              {trend.value}
            </span>
          </div>
        )}
      </div>

      {/* Footer Comparison Subtitle */}
      {subtitle && (
        <div className="mt-5 pt-3.5 border-t border-white/10 flex items-center justify-between text-xs">
          <span className={cn('line-clamp-1 font-medium', style.subtitle)}>
            {subtitle}
          </span>
        </div>
      )}
    </div>
  );
}
