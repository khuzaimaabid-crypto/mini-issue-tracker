import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()], // Allows you to write jsx and use react features
  resolve: {             // Path aliasing
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true,   // Allows access from outside container
    port: 5173,
    watch: {
      usePolling: true   //Watces for file changes in Docker environments
    }
  },
  test: {         // Test configuration for Vitest
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.js',
    coverage: {
      enabled: false,  
      provider: 'v8',
      reporter: ['text', 'html', 'json', 'lcov'], 
      reportsDirectory: './coverage',  
      include: ['src/**/*.{js,jsx,ts,tsx}'], 
      exclude: [
        'node_modules/',
        'tests/',
        'src/main.jsx',  // Entry point - hard to test
        'src/**/*.test.{js,jsx,ts,tsx}',  // Don't measure test files
        'src/**/*.spec.{js,jsx,ts,tsx}',  // Don't measure spec files
      ],
      // Optional: Set coverage thresholds (tests fail if below these)
      // thresholds: {
      //   lines: 80,
      //   functions: 80,
      //   branches: 80,
      //   statements: 80
      // }
    }
  }
})