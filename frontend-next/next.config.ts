import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // 启用 standalone 输出（用于 Docker）
  output: 'standalone',
  // 确保构建时正确处理环境变量
  env: {
    NEXT_PUBLIC_ADMIN_API_BASE_URL: process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL || 'http://localhost:8001',
    NEXT_PUBLIC_MINIAPP_API_BASE_URL: process.env.NEXT_PUBLIC_MINIAPP_API_BASE_URL || 'http://localhost:8080',
  },
};

export default nextConfig;
