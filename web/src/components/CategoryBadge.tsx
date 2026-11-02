import React from 'react';
import { cn } from '@/lib/utils';
import type { CategoryBrief } from '@/types/api';

interface CategoryBadgeProps {
  category: CategoryBrief | string;
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
    bgClass: 'bg-green-50',
    textClass: 'text-green-800',
    borderClass: 'border-green-200',
    dotClass: 'bg-[#16a34a]',
    hex: '#16a34a',
  },
  'Plastic Waste': {
    bgClass: 'bg-sky-50',
    textClass: 'text-sky-800',
    borderClass: 'border-sky-200',
    dotClass: 'bg-[#0284c7]',
    hex: '#0284c7',
  },
  'Paper Waste': {
    bgClass: 'bg-amber-50',
    textClass: 'text-amber-800',
    borderClass: 'border-amber-200',
    dotClass: 'bg-[#d97706]',
    hex: '#d97706',
  },
};

export default function CategoryBadge({
  category,
  size = 'md',
  className,
  showDot = true,
}: CategoryBadgeProps) {
  const categoryName = typeof category === 'string' ? category : category.name;
  const customBadgeColor = typeof category === 'object' ? category.badge_color : undefined;

  const styleConfig = defaultCategoryStyles[categoryName] || {
    bgClass: 'bg-slate-50',
    textClass: 'text-slate-800',
    borderClass: 'border-slate-200',
    dotClass: 'bg-slate-500',
    hex: '#64748b',
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
        'inline-flex items-center rounded-md border tracking-wide transition-colors',
        styleConfig.bgClass,
        styleConfig.textClass,
        styleConfig.borderClass,
        sizeClasses[size],
        className
      )}
      data-testid="category-badge"
    >
      {showDot && (
        <span
          className={cn('rounded-full shrink-0', styleConfig.dotClass, dotSizes[size])}
          style={customBadgeColor ? { backgroundColor: customBadgeColor } : undefined}
          aria-hidden="true"
        />
      )}
      <span>{categoryName}</span>
    </span>
  );
}
