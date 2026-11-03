import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface StatCardTrend {
  value: string;
  isPositive?: boolean;
}

export interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon | React.ElementType;
  trend?: StatCardTrend;
  variant?: 'default' | 'amber' | 'blue' | 'emerald' | 'slate';
  isLoading?: boolean;
  className?: string;
}

const variantStyles = {
  default: {
    iconBg: 'bg-slate-100 text-slate-700 border-slate-200/80',
    cardBorder: 'hover:border-slate-300',
  },
  slate: {
    iconBg: 'bg-slate-100 text-slate-700 border-slate-200/80',
    cardBorder: 'hover:border-slate-300',
  },
  amber: {
    iconBg: 'bg-amber-50 text-amber-600 border-amber-200/80',
    cardBorder: 'hover:border-amber-300',
  },
  blue: {
    iconBg: 'bg-blue-50 text-blue-600 border-blue-200/80',
    cardBorder: 'hover:border-blue-300',
  },
  emerald: {
    iconBg: 'bg-emerald-50 text-emerald-600 border-emerald-200/80',
    cardBorder: 'hover:border-emerald-300',
  },
};

export default function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  variant = 'default',
  isLoading = false,
  className,
}: StatCardProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          'rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-[0_2px_10px_-3px_rgba(6,78,59,0.05)] animate-pulse',
          className
        )}
        data-testid="stat-card-skeleton"
      >
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="h-4 w-28 rounded bg-slate-200" />
            <div className="h-8 w-20 rounded bg-slate-200" />
          </div>
          <div className="h-12 w-12 rounded-xl bg-slate-200" />
        </div>
        <div className="mt-4 flex items-center gap-2">
          <div className="h-3.5 w-36 rounded bg-slate-100" />
        </div>
      </div>
    );
  }

  const Icon = icon;
  const currentVariant = variantStyles[variant] || variantStyles.default;

  return (
    <div
      className={cn(
        'group relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-[0_2px_10px_-3px_rgba(6,78,59,0.05)] transition-all duration-200 hover:shadow-[0_8px_20px_-4px_rgba(6,78,59,0.08)] hover:-translate-y-0.5',
        currentVariant.cardBorder,
        className
      )}
      data-testid="stat-card"
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="font-sans text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</p>
          <div className="font-heading text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
            {value}
          </div>
        </div>
        <div
          className={cn(
            'flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border transition-transform duration-200 group-hover:scale-105',
            currentVariant.iconBg
          )}
          aria-hidden="true"
        >
          <Icon className="h-6 w-6" />
        </div>
      </div>

      {(subtitle || trend) && (
        <div className="mt-4 flex items-center gap-2 text-xs">
          {trend && (
            <span
              className={cn(
                'inline-flex items-center font-semibold rounded-md px-1.5 py-0.5 font-mono text-[11px]',
                trend.isPositive !== false
                  ? 'bg-emerald-50 text-emerald-700'
                  : 'bg-rose-50 text-rose-700'
              )}
            >
              {trend.value}
            </span>
          )}
          {subtitle && (
            <span className="text-slate-500 line-clamp-1">{subtitle}</span>
          )}
        </div>
      )}
    </div>
  );
}
