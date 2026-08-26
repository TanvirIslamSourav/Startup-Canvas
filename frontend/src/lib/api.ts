/**
 * Tiny typed fetch wrapper. All API routes are namespaced under
 * `/api/v1`; the dev server proxies that path to the FastAPI service.
 */
const BASE_URL = '/api/v1';

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null>;
  signal?: AbortSignal;
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const url = new URL(BASE_URL + path, window.location.origin);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null || value === '') continue;
      url.searchParams.set(key, String(value));
    }
  }
  return url.pathname + url.search;
}

export async function apiRequest<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, query, signal } = opts;
  const init: RequestInit = {
    method,
    headers: { Accept: 'application/json' },
    signal,
    credentials: 'include',
  };
  if (body !== undefined) {
    (init.headers as Record<string, string>)['Content-Type'] = 'application/json';
    init.body = JSON.stringify(body);
  }
  const res = await fetch(buildUrl(path, query), init);
  if (!res.ok) {
    let payload: { error?: { code?: string; message?: string } } = {};
    try {
      payload = await res.json();
    } catch {
      // ignore JSON parse failures
    }
    throw new ApiError(
      res.status,
      payload.error?.code ?? 'http_error',
      payload.error?.message ?? res.statusText,
    );
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}