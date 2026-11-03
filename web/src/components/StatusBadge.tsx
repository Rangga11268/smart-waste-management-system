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
    containerClass: 'bg-amber-50/90 text-amber-700 border-amber-200/80',
    dotClass: 'bg-amber-500',
    pingClass: 'bg-amber-400',
    label: 'Pending',
  },
  'In Progress': {
    containerClass: 'bg-blue-50/90 text-blue-700 border-blue-200/80',
    dotClass: 'bg-blue-500',
    pingClass: 'bg-blue-400',
    label: 'In Progress',
  },
  Completed: {
    containerClass: 'bg-emerald-50/90 text-emerald-700 border-emerald-200/80',
    dotClass: 'bg-emerald-500',
    pingClass: 'bg-emerald-400',
    label: 'Completed',
  },
  Rejected: {
    containerClass: 'bg-rose-50/90 text-rose-700 border-rose-200/80',
    dotClass: 'bg-rose-500',
    pingClass: 'bg-rose-400',
    label: 'Rejected',
  },
};

export default function StatusBadge({
  status,
  size = 'md',
  className,
  showDot = true,
}: StatusBadgeProps) {
  const config = statusConfig[status] || {
    containerClass: 'bg-slate-50 text-slate-700 border-slate-200',
    dotClass: 'bg-slate-400',
    pingClass: 'bg-slate-300',
    label: status,
  };

  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5 font-medium',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3 py-1.5 gap-2 font-medium',
  };

  const dotSizes = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border tracking-wide transition-colors shadow-[0_1px_2px_rgba(0,0,0,0.03)]',
        config.containerClass,
        sizeClasses[size],
        className
      )}
      data-testid="status-badge"
    >
      {showDot && (
        <span className={cn('relative flex items-center justify-center shrink-0', dotSizes[size])}>
          <span
            className={cn(
              'absolute inline-flex h-full w-full rounded-full opacity-60 animate-ping',
              config.pingClass
            )}
          />
          <span className={cn('relative inline-flex rounded-full', config.dotClass, dotSizes[size])} />
        </span>
      )}
      <span>{config.label}</span>
    </span>
  );
}
