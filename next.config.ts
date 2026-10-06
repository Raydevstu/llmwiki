import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
  transpilePackages: [
    "@repo/design-system",
    "@repo/database",
    "@repo/ai-memory",
  ],
  serverExternalPackages: ["z-ai-web-dev-sdk", "socket.io-client"],
  experimental: {
    serverActions: {
      bodySizeLimit: "5mb",
    },
  },
};

export default nextConfig;
