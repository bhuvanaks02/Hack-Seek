/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
    FRONTEND_URL: process.env.FRONTEND_URL || 'http://localhost:3000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_BASE_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ]
  },
  images: {
    domains: ['localhost', 'devpost.com', 'unstop.com', 'mlh.io', 'hackerearth.com'],
    unoptimized: true,
  },
}

module.exports = nextConfig