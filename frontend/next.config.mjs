/** @type {import('next').NextConfig} */
const BACKEND_URL = process.env.BACKEND_URL || 'https://lms-backend-345468513781.us-central1.run.app';

const nextConfig = {
  rewrites: async () => {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_URL}/:path*`,
      },
    ]
  },
};

export default nextConfig;
