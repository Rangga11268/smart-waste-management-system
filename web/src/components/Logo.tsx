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
      <svg
        width={size}
        height={size}
        viewBox="0 0 256 256"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 transition-transform duration-200 hover:scale-105"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="logoLeafA" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4ADE80" />
            <stop offset="100%" stopColor="#16A34A" />
          </linearGradient>
          <linearGradient id="logoLeafB" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10B981" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>
          <linearGradient id="logoLeafC" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#059669" />
            <stop offset="100%" stopColor="#047857" />
          </linearGradient>
        </defs>
        <g transform="translate(128,128)">
          {/* Leaf 1 (Top) */}
          <path
            d="M 0,-104 C 42,-104 84,-72 84,-24 C 84,16 54,48 16,62 C 34,36 38,10 32,-16 C 26,-42 12,-74 0,-104 Z"
            fill="url(#logoLeafA)"
          />
          <path
            d="M 0,-104 C 18,-70 24,-40 20,-10 C 18,12 8,34 -4,50 C 8,36 14,18 14,-4 C 14,-28 8,-66 0,-104 Z"
            fill="#15803D"
            opacity="0.3"
          />

          {/* Leaf 2 (Bottom Right, 120deg) */}
          <g transform="rotate(120)">
            <path
              d="M 0,-104 C 42,-104 84,-72 84,-24 C 84,16 54,48 16,62 C 34,36 38,10 32,-16 C 26,-42 12,-74 0,-104 Z"
              fill="url(#logoLeafB)"
            />
            <path
              d="M 0,-104 C 18,-70 24,-40 20,-10 C 18,12 8,34 -4,50 C 8,36 14,18 14,-4 C 14,-28 8,-66 0,-104 Z"
              fill="#065F46"
              opacity="0.3"
            />
          </g>

          {/* Leaf 3 (Bottom Left, 240deg) */}
          <g transform="rotate(240)">
            <path
              d="M 0,-104 C 42,-104 84,-72 84,-24 C 84,16 54,48 16,62 C 34,36 38,10 32,-16 C 26,-42 12,-74 0,-104 Z"
              fill="url(#logoLeafC)"
            />
            <path
              d="M 0,-104 C 18,-70 24,-40 20,-10 C 18,12 8,34 -4,50 C 8,36 14,18 14,-4 C 14,-28 8,-66 0,-104 Z"
              fill="#047857"
              opacity="0.4"
            />
          </g>

          {/* Seed core */}
          <circle cx="0" cy="0" r="10" fill="#10B981" />
        </g>
      </svg>

      {showText && (
        <div className="flex flex-col whitespace-nowrap min-w-0">
          <div className="flex items-center gap-1.5">
            <span
              className={cn(
                'text-base sm:text-lg font-extrabold tracking-tight leading-none',
                isInverted ? 'text-white' : 'text-slate-900'
              )}
            >
              SWMS
            </span>
            <span
              className={cn(
                'rounded px-1.5 py-0.5 text-[9px] sm:text-[10px] font-bold tracking-wider uppercase leading-none',
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
              'text-[9px] sm:text-[10px] font-semibold tracking-wider uppercase mt-1 hidden sm:block whitespace-nowrap',
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
