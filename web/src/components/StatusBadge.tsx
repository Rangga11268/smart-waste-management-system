import React from 'react';
import { cn } from '@/lib/utils';
import type { ReportStatus } from '@/types/api';

interface StatusBadgeProps {
  status: ReportStatus | string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showDot?: boolean;
}

const statusConfig: Record<
  string,
  {
    containerClass: string;
    dotClass: string;
    pingClass: string;
    label: string;
  }
> = {
  Pending: {
    containerClass: 'bg-amber-50/90 text-amber-800 border-amber-300',
    dotClass: 'bg-amber-500',
    pingClass: 'bg-amber-400',
    label: 'Menunggu Validasi',
  },
  'In Progress': {
    containerClass: 'bg-blue-50/90 text-blue-800 border-blue-300',
    dotClass: 'bg-blue-500',
    pingClass: 'bg-blue-400',
    label: 'Sedang Ditangani',
  },
  Completed: {
    containerClass: 'bg-emerald-50/90 text-emerald-800 border-emerald-300',
    dotClass: 'bg-emerald-500',
    pingClass: 'bg-emerald-400',
    label: 'Selesai Ditangani',
  },
  Rejected: {
    containerClass: 'bg-rose-50/90 text-rose-800 border-rose-300',
    dotClass: 'bg-rose-500',
    pingClass: 'bg-rose-400',
    label: 'Laporan Ditolak',
  },
};

export default function StatusBadge({
  status,
  size = 'md',
  className,
}: StatusBadgeProps) {
  const config = statusConfig[status] || {
    containerClass: 'bg-slate-50 text-slate-700 border-slate-200',
    dotClass: 'bg-slate-400',
    pingClass: 'bg-slate-300',
    label: status,
  };

  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 font-medium',
    md: 'text-xs px-2.5 py-1 font-medium',
    lg: 'text-sm px-3 py-1.5 font-medium',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md border font-medium tracking-wide transition-colors shadow-2xs',
        config.containerClass,
        sizeClasses[size],
        className
      )}
      data-testid="status-badge"
    >
      <span>{config.label}</span>
    </span>
  );
}
