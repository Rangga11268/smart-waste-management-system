'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  ClipboardList,
  Users,
  ExternalLink,
  X,
  FileText,
  LogOut,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/lib/auth';
import Logo from '@/components/Logo';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
  external?: boolean;
}

const navItems: NavItem[] = [
  {
    name: 'Dashboard Overview',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Laporan Sampah',
    href: '/reports',
    icon: ClipboardList,
  },
  {
    name: 'Manajemen Pengguna',
    href: '/users',
    icon: Users,
  },
];

const secondaryNavItems: NavItem[] = [
  {
    name: 'API Documentation',
    href: process.env.NEXT_PUBLIC_API_DOCS_URL || 'http://localhost:8000/docs',
    icon: FileText,
    external: true,
  },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  className?: string;
}

export default function Sidebar({ isOpen = false, onClose, className }: SidebarProps) {
  const pathname = usePathname();
  const { isAdmin, user, logout } = useAuth();

  const isNavActive = (href: string) => {
    if (href === '/dashboard' && pathname === '/dashboard') return true;
    if (href !== '/dashboard' && pathname?.startsWith(href)) return true;
    return false;
  };

  const visibleNavItems = navItems.filter((item) => {
    if (item.href === '/users') return isAdmin;
    return true;
  });

  const initials = user?.full_name
    ? user.full_name
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0])
        .join('')
        .toUpperCase()
    : 'SA';

  const navContent = (
    <div className="flex h-full flex-col justify-between bg-slate-900 text-slate-100">
      <div>
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-5">
          <Link href="/dashboard" className="flex items-center group">
            <Logo size={36} showText={true} variant="inverted" />
          </Link>
          {onClose && (
            <button
              onClick={onClose}
              className="rounded-xl p-2 text-slate-400 hover:bg-slate-800 hover:text-white md:hidden transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-label="Tutup navigasi"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Navigation Sections */}
        <div className="px-4 py-6 space-y-6">
          <div>
            <p className="px-3 pb-2.5 text-[11px] font-bold uppercase tracking-wider text-slate-300">
              Menu Utama
            </p>
            <nav className="space-y-1.5">
              {visibleNavItems.map((item) => {
                const active = isNavActive(item.href);
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => onClose?.()}
                    className={cn(
                      'group flex items-center justify-between rounded-xl px-3.5 py-3 text-sm font-semibold transition-all duration-200 min-h-[44px]',
                      active
                        ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/25'
                        : 'text-slate-200 hover:bg-slate-800 hover:text-white'
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <Icon
                        className={cn(
                          'h-5 w-5 shrink-0 transition-colors',
                          active ? 'text-white' : 'text-slate-300 group-hover:text-emerald-400'
                        )}
                      />
                      <span>{item.name}</span>
                    </div>
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Secondary / Dev Tools */}
          <div className="pt-4 border-t border-slate-800">
            <p className="px-3 pb-2.5 text-[11px] font-bold uppercase tracking-wider text-slate-300">
              Pengembang & Sistem
            </p>
            <nav className="space-y-1.5">
              {secondaryNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <a
                    key={item.name}
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-200 hover:bg-slate-800 hover:text-white transition-colors min-h-[44px]"
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="h-5 w-5 shrink-0 text-slate-300 group-hover:text-emerald-400" />
                      <span>{item.name}</span>
                    </div>
                    <ExternalLink className="h-4 w-4 shrink-0 text-slate-400 group-hover:text-slate-200" />
                  </a>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* Footer User Profile & System Status */}
      <div className="border-t border-slate-800 p-4 space-y-3">
        {user && (
          <div className="flex items-center justify-between rounded-xl bg-slate-800/90 border border-slate-700 p-3 shadow-sm">
            <div className="flex items-center gap-3 min-w-0">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-700 font-bold text-white text-xs border border-slate-600">
                {initials}
              </div>
              <div className="min-w-0">
                <p className="truncate text-xs font-bold text-white tracking-tight">
                  {user.full_name || 'Admin SWMS'}
                </p>
                <p className="text-[11px] text-slate-300 capitalize">
                  {user.role === 'admin' ? 'Super Admin' : 'Warga Pelapor'}
                </p>
              </div>
            </div>
            {logout && (
              <button
                type="button"
                onClick={logout}
                title="Keluar dari akun"
                className="rounded-lg p-2 text-slate-400 hover:bg-rose-500/20 hover:text-rose-300 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                aria-label="Logout"
              >
                <LogOut className="h-4 w-4" />
              </button>
            )}
          </div>
        )}

        <div className="flex items-center justify-between px-2 text-xs">
          <span className="font-semibold text-slate-400 text-[11px]">Backend API</span>
          <span className="font-mono text-[11px] font-semibold text-emerald-400">
            Connected (WIB)
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed Push Sidebar (Statis pada Layar Lebar) */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-slate-800 bg-slate-900 shadow-xl md:block',
          className
        )}
      >
        {navContent}
      </aside>

      {/* Mobile Drawer Backdrop (Hanya di Bawah Breakpoint md) */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/70 backdrop-blur-xs transition-opacity md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Mobile Slide-out Drawer */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 transform bg-slate-900 shadow-2xl transition-transform duration-300 ease-in-out md:hidden',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {navContent}
      </div>
    </>
  );
}
