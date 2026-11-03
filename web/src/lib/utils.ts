import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges class names safely with Tailwind conflict resolution
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Format GPS coordinates into readable standard lat, long string
 */
export function formatGpsCoordinates(lat: number, lng: number): string {
  if (typeof lat !== 'number' || typeof lng !== 'number') return 'N/A';
  return `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
}

/**
 * Generate Google Maps URL from latitude and longitude
 */
export function getGoogleMapsUrl(lat: number, lng: number): string {
  return `https://www.google.com/maps?q=${lat},${lng}`;
}

/**
 * Normalizes date strings to UTC ISO format if offset or Z is omitted.
 */
function parseSafeDate(dateString: string): Date {
  const s = dateString.trim();
  const normalized = s.endsWith('Z') || s.includes('+') || (s.length > 10 && s.substring(10).includes('-'))
    ? s
    : `${s}Z`;
  return new Date(normalized);
}

/**
 * Format ISO datetime string into human readable locale string (WIB)
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '-';
  try {
    const d = parseSafeDate(dateString);
    if (isNaN(d.getTime())) return dateString;
    return new Intl.DateTimeFormat('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(d);
  } catch {
    return dateString;
  }
}

/**
 * Formats ISO datetime string into human-friendly relative time (e.g. "Baru saja", "5 menit lalu")
 */
export function formatRelativeTime(dateString: string | null | undefined): string {
  if (!dateString) return '-';
  try {
    const d = parseSafeDate(dateString);
    if (isNaN(d.getTime())) return dateString;
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffSec = Math.floor(diffMs / 1000);

    if (diffSec < 60) return 'Baru saja';
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin} menit lalu`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour} jam lalu`;
    const diffDays = Math.floor(diffHour / 24);
    if (diffDays === 1) return 'Kemarin';
    if (diffDays < 7) return `${diffDays} hari lalu`;
    return formatDate(dateString);
  } catch {
    return dateString;
  }
}

/**
 * Format confidence or percentage value to readable 0.00%
 */
export function formatPercentage(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return '0%';
  // If val is between 0 and 1, multiply by 100
  const normalized = val <= 1 && val > 0 ? val * 100 : val;
  return `${normalized.toFixed(1)}%`;
}
