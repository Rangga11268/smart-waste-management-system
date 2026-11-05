import React from 'react';
import { cn } from '@/lib/utils';

export interface LogoProps {
  size?: number;
  className?: string;
  showText?: boolean;
  variant?: 'default' | 'inverted';
}

export default function Logo({
  size = 36,
  className,
  showText = true,
  variant = 'default',
}: LogoProps) {
  const isInverted = variant === 'inverted';

  return (
    <div className={cn('inline-flex items-center gap-2.5 sm:gap-3 select-none shrink-0', className)}>
      {/* High-Contrast Bold Eco Emblem Tile matching Image 4 */}
      <div
        className={cn(
          'flex items-center justify-center rounded-xl shrink-0 transition-transform duration-200 hover:scale-105 shadow-xs',
          isInverted
            ? 'bg-gradient-to-br from-emerald-500 to-teal-700 text-white border border-emerald-400/30'
            : 'bg-gradient-to-br from-emerald-600 via-emerald-600 to-teal-700 text-white shadow-emerald-700/20'
        )}
        style={{ width: size, height: size }}
      >
        <svg
          width={Math.round(size * 0.62)}
          height={Math.round(size * 0.62)}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.5 10-10 10Z"
            fill="white"
            fillOpacity="0.95"
          />
          <path
            d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"
            stroke="white"
            strokeWidth="2.2"
            strokeLinecap="round"
          />
        </svg>
      </div>

      {showText && (
        <div className="flex flex-col whitespace-nowrap min-w-0">
          <div className="flex items-center gap-1.5">
            <span
              className={cn(
                'text-lg font-extrabold tracking-tight leading-none font-sans',
                isInverted ? 'text-white' : 'text-slate-900'
              )}
            >
              SWMS
            </span>
            <span
              className={cn(
                'rounded px-1.5 py-0.5 text-[10px] font-bold tracking-wider uppercase leading-none',
                isInverted
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/30'
                  : 'bg-emerald-50 text-emerald-700 border border-emerald-200/80'
              )}
            >
              ECO
            </span>
          </div>
          <span
            className={cn(
              'text-[10px] font-semibold tracking-wider uppercase mt-1',
              isInverted ? 'text-slate-300' : 'text-slate-500'
            )}
          >
            Smart Waste Management
          </span>
        </div>
      )}
    </div>
  );
}
