import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server runs on port 5173, which the backend's CORS settings already allow.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, host: true },
});
