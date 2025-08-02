/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  },
  
  // Image optimization
  images: {
    domains: [
      'tg-external-entities-prod.s3.me-south-1.amazonaws.com',
      'localhost',
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'tg-external-entities-prod.s3.me-south-1.amazonaws.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
  
  // Experimental features (appDir is now stable in Next.js 14)
  experimental: {
    // Add future experimental features here if needed
  },
  
  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig