import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ command, mode }) => {
  if (command === 'build' && mode === 'production') {
    const env = loadEnv(mode, process.cwd(), 'VITE_');
    const apiBaseURL = env.VITE_API_BASE_URL?.trim();
    if (!apiBaseURL) {
      throw new Error('Set VITE_API_BASE_URL to your HTTPS backend URL before building for production.');
    }
    let apiURL: URL;
    try {
      apiURL = new URL(apiBaseURL);
    } catch {
      throw new Error('VITE_API_BASE_URL must be a valid absolute HTTPS URL.');
    }
    const localHosts = ['localhost', '0.0.0.0', '[::1]'];
    if (
      apiURL.protocol !== 'https:' ||
      localHosts.includes(apiURL.hostname.toLowerCase()) ||
      apiURL.hostname.startsWith('127.') ||
      apiURL.hostname.toLowerCase().endsWith('.localhost') ||
      apiURL.username || apiURL.password
    ) {
      throw new Error('VITE_API_BASE_URL must point to a public HTTPS backend without embedded credentials.');
    }
  }
  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: true,
    },
  };
});
