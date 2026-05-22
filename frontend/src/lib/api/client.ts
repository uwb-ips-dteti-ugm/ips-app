import type { ErrorResponse } from "./common";

type ApiQueryValue = boolean | number | string | null | undefined;

export type ApiQuery = Record<string, ApiQueryValue>;

export type ApiRequestOptions = Omit<
  RequestInit,
  "body" | "headers" | "method"
> & {
  accessToken?: string;
  baseUrl?: string | URL;
  headers?: HeadersInit;
};

type RequestOptions = ApiRequestOptions & {
  json?: unknown;
  method?: string;
  query?: ApiQuery;
};

export const apiBaseUrl =
  process.env.IPS_API_BASE_URL ??
  process.env.NEXT_PUBLIC_IPS_API_BASE_URL ??
  "http://localhost:8000";

export class ApiError extends Error {
  readonly body: unknown;
  readonly status: number;

  constructor(status: number, body: unknown) {
    super(getApiErrorMessage(status, body));
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export async function requestJson<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const response = await request(path, options);
  return (await response.json()) as T;
}

export async function requestText(
  path: string,
  options: RequestOptions = {},
): Promise<string> {
  const response = await request(path, options);
  return response.text();
}

async function request(
  path: string,
  {
    accessToken,
    baseUrl = apiBaseUrl,
    headers,
    json,
    method = "GET",
    query,
    ...init
  }: RequestOptions,
): Promise<Response> {
  const requestHeaders = new Headers(headers);

  if (accessToken) {
    requestHeaders.set("Authorization", `Bearer ${accessToken}`);
  }

  if (json !== undefined && !requestHeaders.has("Content-Type")) {
    requestHeaders.set("Content-Type", "application/json");
  }

  const response = await fetch(buildUrl(path, query, baseUrl), {
    ...init,
    body: json === undefined ? undefined : JSON.stringify(json),
    cache: init.cache ?? "no-store",
    headers: requestHeaders,
    method,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await readBody(response));
  }

  return response;
}

function buildUrl(
  path: string,
  query: ApiQuery | undefined,
  baseUrl: string | URL,
): URL {
  const url = new URL(path, baseUrl);

  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== null && value !== undefined) {
      url.searchParams.set(key, String(value));
    }
  }

  return url;
}

async function readBody(response: Response): Promise<unknown> {
  const body = await response.text();
  if (!body) {
    return undefined;
  }

  try {
    return JSON.parse(body) as unknown;
  } catch {
    return body;
  }
}

function getApiErrorMessage(status: number, body: unknown): string {
  if (isErrorResponse(body)) {
    return body.error;
  }

  if (typeof body === "string" && body) {
    return body;
  }

  return `API request failed with status ${status}.`;
}

function isErrorResponse(body: unknown): body is ErrorResponse {
  return (
    typeof body === "object" &&
    body !== null &&
    "error" in body &&
    typeof body.error === "string"
  );
}
