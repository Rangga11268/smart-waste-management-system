import assert from 'node:assert';
import { cn, formatGpsCoordinates, getGoogleMapsUrl, formatPercentage, formatDate } from '../src/lib/utils.ts';

console.log('--- Verifying M1 Utilities and Logic ---');

// 1. cn helper test
assert.strictEqual(cn('px-2', 'py-1'), 'px-2 py-1');
assert.strictEqual(cn('px-2', 'px-4'), 'px-4'); // Tailwind merge conflict resolution
assert.strictEqual(cn('text-red-500', false && 'hidden', null, undefined, 'font-bold'), 'text-red-500 font-bold');
console.log('✓ cn() helper passed');

// 2. formatGpsCoordinates test
assert.strictEqual(formatGpsCoordinates(-6.208763, 106.845599), '-6.2088, 106.8456');
assert.strictEqual(formatGpsCoordinates(0, 0), '0.0000, 0.0000');
assert.strictEqual(formatGpsCoordinates(null, undefined), 'N/A');
console.log('✓ formatGpsCoordinates() passed');

// 3. getGoogleMapsUrl test
assert.strictEqual(getGoogleMapsUrl(-6.2088, 106.8456), 'https://www.google.com/maps?q=-6.2088,106.8456');
console.log('✓ getGoogleMapsUrl() passed');

// 4. formatPercentage test
assert.strictEqual(formatPercentage(0.9421), '94.2%');
assert.strictEqual(formatPercentage(85.5), '85.5%');
assert.strictEqual(formatPercentage(1), '100.0%');
assert.strictEqual(formatPercentage(null), '0%');
console.log('✓ formatPercentage() passed');

// 5. formatDate test
const iso = '2026-11-02T10:15:30Z';
const formatted = formatDate(iso);
assert.ok(formatted.length > 5, 'Formatted date should not be empty');
assert.strictEqual(formatDate(null), '-');
assert.strictEqual(formatDate('invalid-date'), 'invalid-date');
console.log('✓ formatDate() passed');

console.log('--- All M1 Unit Checks Passed Successfully! ---');
