import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// Khi chạy `npm run dev`, các yêu cầu /chat và /health được chuyển tiếp tới api.py.
// Đổi cổng bằng cách tạo file .env với dòng: VITE_BACKEND=http://127.0.0.1:5000
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_BACKEND || "http://127.0.0.1:8000";
  return {
    plugins: [react()],
    server: {
      proxy: {
        "/chat": { target, changeOrigin: true },
        "/health": { target, changeOrigin: true },
      },
    },
  };
});
