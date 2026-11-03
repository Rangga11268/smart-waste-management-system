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
 * Format ISO datetime string into human readable locale string
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '-';
  try {
    const d = new Date(dateString);
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
 * Format confidence or percentage value to readable 0.00%
 */
export function formatPercentage(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return '0%';
  // If val is between 0 and 1, multiply by 100
  const normalized = val <= 1 && val > 0 ? val * 100 : val;
  return `${normalized.toFixed(1)}%`;
}
