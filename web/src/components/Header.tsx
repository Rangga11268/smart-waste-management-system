'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Menu,
  ChevronRight,
  LogOut,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { UserProfile } from '@/types/api';

interface HeaderProps {
  onOpenSidebar?: () => void;
  user?: UserProfile | null;
  onLogout?: () => void;
  className?: string;
}

export default function Header({ onOpenSidebar, user, onLogout, className }: HeaderProps) {
  const pathname = usePathname();
  const [healthStatus, setHealthStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  // Ping backend health check endpoint
  useEffect(() => {
    let isMounted = true;

    async function checkHealth() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
        // Backend root health is at http://localhost:8000/health
        const baseOrigin = apiUrl.replace(/\/api\/v1\/?$/, '');
        const res = await fetch(`${baseOrigin}/health`, {
          method: 'GET',
          cache: 'no-store',
        });
        if (isMounted) {
          if (res.ok) {
            setHealthStatus('online');
          } else {
            setHealthStatus('offline');
          }
          setLastCheck(new Date());
        }
      } catch {
        if (isMounted) {
          setHealthStatus('offline');
          setLastCheck(new Date());
        }
      }
    }

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Compute breadcrumbs
  const getBreadcrumbs = () => {
    const paths = (pathname || '').split('/').filter(Boolean);
    if (paths.length === 0) {
      return [{ label: 'Dashboard', href: '/dashboard' }];
    }

    const breadcrumbs = [];
    let currentPath = '';

    for (const segment of paths) {
      currentPath += `/${segment}`;
      let label = segment.charAt(0).toUpperCase() + segment.slice(1);
      if (segment === 'dashboard') label = 'Dashboard';
      else if (segment === 'reports') label = 'Laporan Sampah';
      else if (segment === 'users') label = 'Manajemen Pengguna';

      breadcrumbs.push({ label, href: currentPath });
    }
    return breadcrumbs;
  };

  const breadcrumbs = getBreadcrumbs();
  const displayName = user?.full_name || 'Admin SWMS';
  const displayRole = user?.role ? (user.role === 'admin' ? 'Super Admin' : 'Petugas') : 'Administrator';

  return (
    <header
      className={cn(
        'sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur-xs sm:px-6 lg:px-8',
        className
      )}
    >
      <div className="flex items-center gap-3">
        {/* Mobile Hamburger Toggle */}
        <button
          onClick={onOpenSidebar}
          className="rounded-xl p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800 md:hidden transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
          aria-label="Buka menu navigasi"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="flex items-center space-x-1.5 text-sm">
          <Link
            href="/dashboard"
            className="font-medium text-slate-500 hover:text-emerald-600 transition-colors"
          >
            SWMS
          </Link>
          {breadcrumbs.map((crumb, idx) => (
            <React.Fragment key={crumb.href}>
              <ChevronRight className="h-4 w-4 text-slate-400 shrink-0" />
              {idx === breadcrumbs.length - 1 ? (
                <span className="font-heading font-semibold text-slate-900">{crumb.label}</span>
              ) : (
                <Link
                  href={crumb.href}
                  className="font-medium text-slate-500 hover:text-emerald-600 transition-colors"
                >
                  {crumb.label}
                </Link>
              )}
            </React.Fragment>
          ))}
        </nav>
      </div>

      {/* Right Actions: Live API Health & User Profile */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Live Backend Health Indicator */}
        <div
          className={cn(
            'hidden sm:flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium transition-colors',
            healthStatus === 'online' && 'border-emerald-200 bg-emerald-50 text-emerald-700',
            healthStatus === 'offline' && 'border-rose-200 bg-rose-50 text-rose-700',
            healthStatus === 'checking' && 'border-amber-200 bg-amber-50 text-amber-700'
          )}
          title={`Backend status: ${healthStatus}${lastCheck ? ` (Dicek ${lastCheck.toLocaleTimeString()})` : ''}`}
        >
          <span
            className={cn(
              'h-2 w-2 rounded-full',
              healthStatus === 'online' && 'bg-emerald-500 animate-pulse',
              healthStatus === 'offline' && 'bg-rose-500',
              healthStatus === 'checking' && 'bg-amber-500 animate-pulse'
            )}
          />
          <span className="font-mono uppercase tracking-wider text-[11px]">
            {healthStatus === 'online'
              ? 'API Online'
              : healthStatus === 'offline'
              ? 'API Offline'
              : 'Checking API'}
          </span>
        </div>

        {/* User Summary Widget (Clean & Non-Redundant) */}
        <div className="flex items-center gap-2.5 border-l border-slate-200 pl-3 sm:pl-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 font-heading text-xs font-extrabold text-slate-800 border border-slate-200 shadow-2xs">
            {displayName
              .split(' ')
              .map((n) => n[0])
              .slice(0, 2)
              .join('')
              .toUpperCase()}
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-bold text-slate-900 leading-tight">{displayName}</div>
            <div className="text-[11px] font-medium text-slate-500 capitalize">{displayRole}</div>
          </div>

          {/* Logout Button */}
          {onLogout && (
            <button
              onClick={onLogout}
              className="ml-1 rounded-xl p-2 text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
              title="Keluar / Logout"
              aria-label="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
