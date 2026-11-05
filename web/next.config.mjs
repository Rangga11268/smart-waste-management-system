/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
        pathname: '/**',
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/backend-api/:path*',
        destination: 'https://smart-waste-management-system-production.up.railway.app/api/v1/:path*',
      },
      {
        source: '/backend-uploads/:path*',
        destination: 'https://smart-waste-management-system-production.up.railway.app/uploads/:path*',
      },
      {
        source: '/docs',
        destination: 'https://smart-waste-management-system-production.up.railway.app/docs',
      },
      {
        source: '/openapi.json',
        destination: 'https://smart-waste-management-system-production.up.railway.app/openapi.json',
      },
    ];
  },
};

export default nextConfig;
