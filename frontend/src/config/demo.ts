/**
 * DEMO mode configuration.
 *
 * When true, the app uses built-in sample assets instead of calling
 * an external AI API. This ensures the full pipeline is runnable
 * without any API keys for judging / review.
 *
 * Controlled by VITE_DEMO_MODE env var; defaults to true.
 */
export const DEMO_MODE: boolean =
  import.meta.env.VITE_DEMO_MODE !== 'false';

/** Backend API base URL — proxied via Vite in dev */
export const API_BASE = '/api';
