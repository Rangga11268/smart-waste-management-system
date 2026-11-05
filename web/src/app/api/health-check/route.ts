import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  const envUrl = process.env.NEXT_PUBLIC_API_URL || 'https://smart-waste-management-system-production.up.railway.app';
  const clean = envUrl.trim().replace(/\/+$/, '');
  const base = clean.replace(/\/api\/v1\/?$/, '');
  const targetUrl = `${base}/health`;

  try {
    const start = Date.now();
    const res = await fetch(targetUrl, {
      signal: AbortSignal.timeout(8000),
      cache: 'no-store',
    });
    const duration = Date.now() - start;
    const data = await res.json().catch(() => null);

    return NextResponse.json({
      status: 'ok',
      railwayHttpStatus: res.status,
      railwayOk: res.ok,
      latencyMs: duration,
      data,
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      {
        status: 'error',
        message: 'Failed to connect to backend',
        targetUrl,
        error: errorMsg,
      },
      { status: 502 }
    );
  }
}
