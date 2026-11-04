'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import { AuthProvider, useAuth } from '@/lib/auth';
import { AlertCircle, Loader2, X } from 'lucide-react';

function DashboardShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isLoading, isAuthenticated, logout } = useAuth();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [accessNotice, setAccessNotice] = useState<string | null>(null);

  // Route protection and Role-Based Access Control (RBAC) guard
  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      router.replace('/login');
      return;
    }

    // Role-based access control (RBAC):
    // Citizens ('user' role) have full access to /dashboard (public transparency) and /reports.
    // Only /users (User Management) is strictly restricted to Administrators.
    if (user?.role !== 'admin') {
      const isRestricted = pathname === '/users' || pathname?.startsWith('/users/');

      if (isRestricted) {
        setAccessNotice(
          'Akses Terbatas: Menu Manajemen Pengguna hanya dapat diakses oleh Administrator.'
        );
        router.replace('/dashboard');
      }
    }
  }, [isLoading, isAuthenticated, user, pathname, router]);

  // Loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-surface-ground">
        <div className="flex flex-col items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-emerald-200 bg-emerald-50 text-emerald-600 shadow-xs">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
          <p className="font-sans text-sm font-semibold text-slate-700">
            Memuat Sistem SWMS...
          </p>
          <p className="text-xs text-slate-400">Memverifikasi sesi pengguna</p>
        </div>
      </div>
    );
  }

  // Prevent flicker while redirecting unauthenticated users
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-surface-ground">
      {/* Sidebar Navigation */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main App Container with Push Margin on Tablets & Desktop */}
      <div className="flex min-h-screen flex-1 flex-col md:pl-64">
        {/* Top Header Bar */}
        <Header
          onOpenSidebar={() => setSidebarOpen(true)}
          user={user}
          onLogout={logout}
        />

        {/* Access Notice Banner if Citizen attempted to access Admin Route */}
        {accessNotice && (
          <div className="px-4 pt-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 shadow-xs">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-5 w-5 shrink-0 text-amber-600" />
                <p className="font-medium text-xs sm:text-sm">{accessNotice}</p>
              </div>
              <button
                type="button"
                onClick={() => setAccessNotice(null)}
                className="rounded-lg p-1 text-amber-700 hover:bg-amber-100 transition-colors"
                aria-label="Tutup notifikasi"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {/* Page Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <DashboardShell>{children}</DashboardShell>
    </AuthProvider>
  );
}
