import { defineConfig } from 'vitest/config';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig({
  // Vitest ships its own bundled copy of Vite whose `Plugin` type does
  // not match the top-level Vite's Plugin type. Cast the plugin array
  // through unknown to keep tsc -b quiet without losing runtime types.
  plugins: [react() as never],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    css: false,
  },
});
