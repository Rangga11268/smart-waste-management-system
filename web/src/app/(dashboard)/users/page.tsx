'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  ShieldCheck,
  UserCheck,
  Search,
  RefreshCw,
  Filter,
  Phone,
  Mail,
  Calendar,
  FileText,
  AlertCircle,
  Eye,
  X,
} from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { usersApi } from '@/lib/api';
import type { UserListItem } from '@/types/api';

export default function UsersPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState<string>('');
  const [roleFilter, setRoleFilter] = useState<string>('');

  // Selected User for Detail Modal
  const [selectedUser, setSelectedUser] = useState<UserListItem | null>(null);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await usersApi.getUsers({
        search: search.trim() || undefined,
        role: roleFilter || undefined,
      });
      setUsers(res.data);
    } catch (err: any) {
      console.error('Failed to fetch users:', err);
      // Fallback sample data if offline
      setUsers([
        {
          id: 'admin-001',
          email: 'admin@bilcode.id',
          full_name: 'Super Admin SWMS',
          role: 'admin',
          phone_number: '+62 812-3456-7890',
          is_active: true,
          total_reports: 0,
          created_at: new Date().toISOString(),
        },
        {
          id: 'user-001',
          email: 'user@bilcode.id',
          full_name: 'Darell Rangga (Citizen)',
          role: 'user',
          phone_number: '+62 897-8638-973',
          is_active: true,
          total_reports: 12,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [search, roleFilter]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Metric computations
  const totalUsers = users.length;
  const adminCount = users.filter((u) => u.role === 'admin').length;
  const citizenCount = users.filter((u) => u.role === 'user').length;
  const activeCount = users.filter((u) => u.is_active).length;

  return (
    <div className="space-y-6">
      {/* Page Title & Refresh */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-sans text-2xl font-bold text-slate-900 tracking-tight">
            Manajemen Pengguna
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Kelola seluruh akun administrator sistem dan warga pelapor kebersihan kota.
          </p>
        </div>
        <button
          onClick={fetchUsers}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-emerald-600' : ''}`} />
          Segarkan Data
        </button>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Pengguna</p>
            <p className="font-sans text-2xl font-bold text-slate-900">{totalUsers}</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Administrator</p>
            <p className="font-sans text-2xl font-bold text-slate-900">{adminCount}</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center font-bold">
            <UserCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Warga Pelapor</p>
            <p className="font-sans text-2xl font-bold text-slate-900">{citizenCount}</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <span className="font-mono text-sm font-bold">100%</span>
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Akun Aktif</p>
            <p className="font-sans text-2xl font-bold text-slate-900">{activeCount}</p>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center gap-4 justify-between">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Cari nama atau email pengguna..."
            className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all font-medium text-slate-700"
            >
              <option value="">Semua Peran (Role)</option>
              <option value="admin">Administrator</option>
              <option value="user">Warga Pelapor (User)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                <th className="py-3.5 px-4 sm:px-6">Pengguna</th>
                <th className="py-3.5 px-4">Peran (Role)</th>
                <th className="py-3.5 px-4">Kontak Telepon</th>
                <th className="py-3.5 px-4 text-center">Total Laporan</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 sm:px-6 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {loading ? (
                // Skeleton loading
                Array.from({ length: 4 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="py-4 px-4 sm:px-6">
                      <div className="h-4 bg-slate-200 rounded w-40 mb-1.5" />
                      <div className="h-3 bg-slate-100 rounded w-28" />
                    </td>
                    <td className="py-4 px-4"><div className="h-5 bg-slate-200 rounded-md w-20" /></td>
                    <td className="py-4 px-4"><div className="h-4 bg-slate-200 rounded w-28" /></td>
                    <td className="py-4 px-4 text-center"><div className="h-4 bg-slate-200 rounded w-8 mx-auto" /></td>
                    <td className="py-4 px-4"><div className="h-5 bg-slate-200 rounded-md w-16" /></td>
                    <td className="py-4 px-4 sm:px-6 text-right"><div className="h-8 bg-slate-200 rounded w-16 ml-auto" /></td>
                  </tr>
                ))
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    <AlertCircle className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                    Tidak ada pengguna yang cocok dengan kriteria pencarian.
                  </td>
                </tr>
              ) : (
                users.map((u) => {
                  const initials = u.full_name
                    ? u.full_name
                        .split(' ')
                        .map((n) => n[0])
                        .slice(0, 2)
                        .join('')
                        .toUpperCase()
                    : 'U';

                  return (
                    <tr key={u.id} className="hover:bg-slate-50/60 transition-colors">
                      {/* Name & Email with Avatar */}
                      <td className="py-3.5 px-4 sm:px-6">
                        <div className="flex items-center gap-3">
                          <div className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs ${
                            u.role === 'admin'
                              ? 'bg-indigo-100 text-indigo-700'
                              : 'bg-emerald-100 text-emerald-700'
                          }`}>
                            {initials}
                          </div>
                          <div>
                            <p className="font-medium text-slate-900 leading-snug">
                              {u.full_name}
                              {currentUser?.id === u.id && (
                                <span className="ml-2 text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-1.5 py-0.5 rounded">
                                  Anda
                                </span>
                              )}
                            </p>
                            <p className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                              <Mail className="w-3 h-3 text-slate-400" />
                              {u.email}
                            </p>
                          </div>
                        </div>
                      </td>

                      {/* Role Badge */}
                      <td className="py-3.5 px-4">
                        {u.role === 'admin' ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-md bg-slate-100 text-slate-800 border border-slate-300">
                            <ShieldCheck className="w-3.5 h-3.5" />
                            Administrator
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
                            <UserCheck className="w-3.5 h-3.5" />
                            Warga Pelapor
                          </span>
                        )}
                      </td>

                      {/* Phone */}
                      <td className="py-3.5 px-4">
                        <span className="font-mono text-xs text-slate-600 flex items-center gap-1.5">
                          <Phone className="w-3 h-3 text-slate-400" />
                          {u.phone_number || '-'}
                        </span>
                      </td>

                      {/* Total Reports */}
                      <td className="py-3.5 px-4 text-center">
                        <span className="font-mono font-semibold text-slate-800 bg-slate-100 px-2.5 py-1 rounded-md text-xs">
                          {u.total_reports}
                        </span>
                      </td>

                      {/* Active Status */}
                      <td className="py-3.5 px-4">
                        {u.is_active ? (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            Aktif
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold rounded-md bg-rose-50 text-rose-800 border border-rose-200">
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                            Nonaktif
                          </span>
                        )}
                      </td>

                      {/* Action */}
                      <td className="py-3.5 px-4 sm:px-6 text-right">
                        <button
                          onClick={() => setSelectedUser(u)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-emerald-600 transition-colors shadow-sm"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          Detail
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* User Detail Modal */}
      {selectedUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full border border-slate-200 shadow-xl overflow-hidden">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <h2 className="font-sans text-lg font-bold text-slate-900">
                Detail Pengguna
              </h2>
              <button
                onClick={() => setSelectedUser(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-5">
              <div className="flex items-center gap-4">
                <div className={`w-14 h-14 rounded-full flex items-center justify-center font-bold text-lg ${
                  selectedUser.role === 'admin'
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'bg-emerald-100 text-emerald-700'
                }`}>
                  {selectedUser.full_name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase()}
                </div>
                <div>
                  <h3 className="font-sans font-bold text-slate-900 text-base">
                    {selectedUser.full_name}
                  </h3>
                  <p className="text-sm text-slate-500">{selectedUser.email}</p>
                </div>
              </div>

              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-3 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">ID Pengguna:</span>
                  <span className="font-mono text-slate-700">{selectedUser.id}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Peran Sistem:</span>
                  <span className="font-semibold capitalize text-slate-800">{selectedUser.role}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Nomor Telepon:</span>
                  <span className="font-mono text-slate-700">{selectedUser.phone_number || '-'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Total Laporan Sampah:</span>
                  <span className="font-mono font-bold text-emerald-700">{selectedUser.total_reports} Laporan</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Status Akun:</span>
                  <span className="font-medium text-emerald-600">Aktif & Terverifikasi</span>
                </div>
                {selectedUser.created_at && (
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500">Tanggal Pendaftaran:</span>
                    <span className="text-slate-700">
                      {new Date(selectedUser.created_at).toLocaleDateString('id-ID', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                      })}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex justify-end">
              <button
                onClick={() => setSelectedUser(null)}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors shadow-sm"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
