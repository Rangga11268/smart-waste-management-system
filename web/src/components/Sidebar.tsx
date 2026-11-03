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

  // Only administrators can see and access User Management
  const visibleNavItems = navItems.filter((item) => {
    if (item.href === '/users') return isAdmin;
    return true;
  });

  const navContent = (
    <div className="flex h-full flex-col justify-between bg-white text-slate-700">
      <div>
        {/* Logo and Brand Header */}
        <div className="flex h-16 items-center justify-between border-b border-slate-200 px-5">
          <Link href="/dashboard" className="flex items-center group">
            <Logo size={34} showText={true} />
          </Link>
          {onClose && (
            <button
              onClick={onClose}
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 lg:hidden"
              aria-label="Tutup navigasi"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Main Navigation Links */}
        <div className="px-4 py-6">
          <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Menu Utama
          </p>
          <nav className="space-y-1">
            {visibleNavItems.map((item) => {
              const active = isNavActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => onClose?.()}
                  className={cn(
                    'group flex items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium transition-all',
                    active
                      ? 'bg-emerald-50 text-emerald-700 font-semibold shadow-xs'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={cn(
                        'h-5 w-5 transition-colors',
                        active ? 'text-emerald-600' : 'text-slate-400 group-hover:text-slate-600'
                      )}
                    />
                    <span>{item.name}</span>
                  </div>
                  {active && (
                    <span className="h-2 w-2 rounded-full bg-emerald-600" aria-hidden="true" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Secondary & Developer Tools */}
          <div className="mt-8 pt-6 border-t border-slate-100">
            <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Pengembang & Sistem
            </p>
            <nav className="space-y-1">
              {secondaryNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <a
                    key={item.name}
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="h-5 w-5 text-slate-400 group-hover:text-slate-600" />
                      <span>{item.name}</span>
                    </div>
                    <ExternalLink className="h-4 w-4 text-slate-400 group-hover:text-slate-600" />
                  </a>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* Footer User Profile & System Status Badge */}
      <div className="border-t border-slate-200/90 p-3 m-3 space-y-2">
        {user && (
          <div className="flex items-center justify-between rounded-xl bg-slate-50 border border-slate-200/80 p-2.5">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-600 font-bold text-white text-xs shadow-xs">
                {user.full_name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div className="min-w-0">
                <p className="truncate text-xs font-bold text-slate-800">{user.full_name}</p>
                <span className="inline-block rounded px-1.5 py-0.2 bg-emerald-100 text-[10px] font-bold text-emerald-800 uppercase tracking-wider">
                  {user.role}
                </span>
              </div>
            </div>
            {logout && (
              <button
                type="button"
                onClick={logout}
                title="Keluar dari akun"
                className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        )}
        <div className="flex items-center justify-between px-2 py-1 text-xs text-slate-500">
          <span className="font-medium text-[11px]">Backend API</span>
          <span className="flex items-center gap-1.5 font-mono text-[11px] text-emerald-700">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            Connected
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
          'fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-slate-200 bg-white lg:block',
          className
        )}
      >
        {navContent}
      </aside>

      {/* Mobile Drawer Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs transition-opacity lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Mobile Slide-out Drawer */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 transform bg-white shadow-2xl transition-transform duration-300 ease-in-out lg:hidden',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {navContent}
      </div>
    </>
  );
}
