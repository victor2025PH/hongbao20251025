import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // 启用 standalone 输出（用于 Docker）
  output: 'standalone',
};

export default nextConfig;
