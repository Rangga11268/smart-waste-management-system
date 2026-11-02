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
    label: string;
  }
> = {
  Pending: {
    containerClass: 'bg-amber-50 text-amber-700 border-amber-200',
    dotClass: 'bg-amber-500',
    label: 'Pending',
  },
  'In Progress': {
    containerClass: 'bg-blue-50 text-blue-700 border-blue-200',
    dotClass: 'bg-blue-500',
    label: 'In Progress',
  },
  Completed: {
    containerClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dotClass: 'bg-emerald-500',
    label: 'Completed',
  },
  Rejected: {
    containerClass: 'bg-rose-50 text-rose-700 border-rose-200',
    dotClass: 'bg-rose-500',
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
    label: status,
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1.5',
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
        'inline-flex items-center rounded-full border tracking-wide transition-colors',
        config.containerClass,
        sizeClasses[size],
        className
      )}
      data-testid="status-badge"
    >
      {showDot && (
        <span
          className={cn('rounded-full shrink-0', config.dotClass, dotSizes[size])}
          aria-hidden="true"
        />
      )}
      <span>{config.label}</span>
    </span>
  );
}
