'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (!token) {
      router.replace('/login');
      return;
    }

    try {
      const user = userStr ? JSON.parse(userStr) : null;
      if (user?.role === 'user') {
        router.replace('/reports');
        return;
      }
    } catch {
      // ignore JSON parse error, proceed to /dashboard
    }

    router.replace('/dashboard');
  }, [router]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-surface-ground">
      <div className="flex flex-col items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-emerald-200 bg-emerald-50 text-emerald-600 shadow-xs">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
        <p className="font-heading text-sm font-semibold text-slate-700">
          Mengarahkan ke SWMS...
        </p>
      </div>
    </div>
  );
}
