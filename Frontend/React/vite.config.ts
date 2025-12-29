import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import path from "path"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),tailwindcss()],
  base: "./",
  build: {
    outDir: path.resolve(__dirname, "../Electron/files"),
    emptyOutDir: true,
  }
})
