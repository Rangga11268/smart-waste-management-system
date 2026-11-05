import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  const targetUrl = 'https://smart-waste-management-system-production.up.railway.app/api/v1/health';
  try {
    const start = Date.now();
    const res = await fetch(targetUrl, {
      signal: AbortSignal.timeout(10000),
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
        message: 'Failed to connect to Railway backend from Vercel',
        targetUrl,
        error: errorMsg,
      },
      { status: 502 }
    );
  }
}
