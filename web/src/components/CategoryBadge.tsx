import React from 'react';
import { cn } from '@/lib/utils';
import type { CategoryBrief } from '@/types/api';

interface CategoryBadgeProps {
  category?: CategoryBrief | string | null;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showDot?: boolean;
}

const defaultCategoryStyles: Record<
  string,
  {
    bgClass: string;
    textClass: string;
    borderClass: string;
    dotClass: string;
    hex: string;
  }
> = {
  'Organic Waste': {
    bgClass: 'bg-emerald-50/90',
    textClass: 'text-emerald-800',
    borderClass: 'border-emerald-200/80',
    dotClass: 'bg-emerald-500',
    hex: '#059669',
  },
  'Plastic Waste': {
    bgClass: 'bg-sky-50/90',
    textClass: 'text-sky-800',
    borderClass: 'border-sky-200/80',
    dotClass: 'bg-sky-500',
    hex: '#0284c7',
  },
  'Paper Waste': {
    bgClass: 'bg-amber-50/90',
    textClass: 'text-amber-800',
    borderClass: 'border-amber-200/80',
    dotClass: 'bg-amber-500',
    hex: '#d97706',
  },
};

export default function CategoryBadge({
  category,
  size = 'md',
  className,
  showDot = false,
}: CategoryBadgeProps) {
  const categoryName =
    typeof category === 'string'
      ? category
      : category?.name || 'Uncategorized';
  const customBadgeColor =
    typeof category === 'object' && category !== null ? category.badge_color : undefined;

  const styleConfig = defaultCategoryStyles[categoryName] || {
    bgClass: 'bg-slate-50',
    textClass: 'text-slate-800',
    borderClass: 'border-slate-200',
    dotClass: 'bg-slate-500',
    hex: '#64748b',
  };

  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 font-medium',
    md: 'text-xs px-2.5 py-1 font-medium',
    lg: 'text-sm px-3 py-1.5 font-medium',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md border tracking-wide transition-colors shadow-[0_1px_2px_rgba(0,0,0,0.02)]',
        styleConfig.bgClass,
        styleConfig.textClass,
        styleConfig.borderClass,
        sizeClasses[size],
        className
      )}
      data-testid="category-badge"
    >
      <span>{categoryName}</span>
    </span>
  );
}
