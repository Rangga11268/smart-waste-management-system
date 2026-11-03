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
  Shield,
  Activity,
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

  const navContent = (
    <div className="flex h-full flex-col justify-between bg-slate-900 text-slate-300">
      <div>
        {/* Brand Header */}
        <div className="flex h-18 items-center justify-between border-b border-slate-800/80 px-6">
          <Link href="/dashboard" className="flex items-center group">
            <Logo size={36} showText={true} variant="inverted" />
          </Link>
          {onClose && (
            <button
              onClick={onClose}
              className="rounded-xl p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden transition-colors"
              aria-label="Tutup navigasi"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Navigation Sections */}
        <div className="px-4 py-6 space-y-6">
          <div>
            <p className="px-3 pb-2.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
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
                      'group flex items-center justify-between rounded-2xl px-3.5 py-3 text-sm font-semibold transition-all duration-200',
                      active
                        ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/25'
                        : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <Icon
                        className={cn(
                          'h-5 w-5 transition-colors',
                          active ? 'text-white' : 'text-slate-400 group-hover:text-emerald-400'
                        )}
                      />
                      <span>{item.name}</span>
                    </div>
                    {active && (
                      <span className="h-2 w-2 rounded-full bg-white shadow-xs" aria-hidden="true" />
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Secondary / Dev Tools */}
          <div className="pt-4 border-t border-slate-800/80">
            <p className="px-3 pb-2.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
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
                    className="group flex items-center justify-between rounded-2xl px-3.5 py-2.5 text-sm font-semibold text-slate-300 hover:bg-slate-800/80 hover:text-white transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="h-5 w-5 text-slate-400 group-hover:text-emerald-400" />
                      <span>{item.name}</span>
                    </div>
                    <ExternalLink className="h-4 w-4 text-slate-400 group-hover:text-slate-200" />
                  </a>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* Footer User Profile & System Status */}
      <div className="border-t border-slate-800/80 p-4 space-y-3">
        {user && (
          <div className="flex items-center justify-between rounded-2xl bg-slate-800/80 border border-slate-700/60 p-3 shadow-md">
            <div className="flex items-center gap-3 min-w-0">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 font-extrabold text-white text-xs shadow-md shadow-emerald-500/20">
                {user.full_name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div className="min-w-0">
                <p className="truncate text-xs font-bold text-white tracking-tight">{user.full_name}</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="inline-block rounded-md px-1.5 py-0.2 bg-emerald-500/20 text-[10px] font-bold text-emerald-300 border border-emerald-400/30 uppercase tracking-wider">
                    {user.role}
                  </span>
                </div>
              </div>
            </div>
            {logout && (
              <button
                type="button"
                onClick={logout}
                title="Keluar dari akun"
                className="rounded-xl p-2 text-slate-400 hover:bg-rose-500/20 hover:text-rose-400 transition-colors"
                aria-label="Logout"
              >
                <LogOut className="h-4 w-4" />
              </button>
            )}
          </div>
        )}

        <div className="flex items-center justify-between px-2 text-xs">
          <span className="font-semibold text-slate-400 text-[11px]">Backend API</span>
          <span className="inline-flex items-center gap-1.5 font-mono text-[11px] font-semibold text-emerald-400">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Connected (WIB)
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-slate-800/90 bg-slate-900 shadow-xl lg:block',
          className
        )}
      >
        {navContent}
      </aside>

      {/* Mobile Drawer Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/70 backdrop-blur-xs transition-opacity lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Mobile Slide-out Drawer */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 transform bg-slate-900 shadow-2xl transition-transform duration-300 ease-in-out lg:hidden',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {navContent}
      </div>
    </>
  );
}
