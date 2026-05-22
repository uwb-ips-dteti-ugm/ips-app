import { NextResponse, type NextRequest } from "next/server";

import {
  ACCESS_TOKEN_COOKIE,
  getAuthCookieOptions,
  REFRESH_TOKEN_COOKIE,
} from "@/lib/auth/cookies";
import { getTokenMaxAgeSeconds, isJwtExpired } from "@/lib/auth/token";

const signInPath = "/sign-in";
const apiBaseUrl =
  process.env.IPS_API_BASE_URL ??
  process.env.NEXT_PUBLIC_IPS_API_BASE_URL ??
  "http://localhost:8000";

type TokenResponse = {
  access_token: string;
  refresh_token: string;
};

export async function proxy(request: NextRequest) {
  const { nextUrl } = request;
  const isSignInPath = nextUrl.pathname === signInPath;

  if (!isPageNavigation(request)) {
    return NextResponse.next();
  }

  const accessToken = request.cookies.get(ACCESS_TOKEN_COOKIE)?.value;
  const hasAccessToken = Boolean(accessToken && !isJwtExpired(accessToken));

  if (hasAccessToken) {
    if (isSignInPath) {
      return NextResponse.redirect(new URL("/", nextUrl));
    }

    return NextResponse.next();
  }

  const refreshedTokens = await refreshAuthTokens(request);
  if (refreshedTokens) {
    const redirectUrl = isSignInPath ? new URL("/", nextUrl) : nextUrl.clone();
    const response = NextResponse.redirect(redirectUrl);

    setAuthCookies(response, refreshedTokens);
    return response;
  }

  if (isSignInPath) {
    return NextResponse.next();
  }

  return NextResponse.redirect(new URL(signInPath, nextUrl));
}

export const config = {
  matcher: ["/", "/admin/:path*", "/sign-in"],
};

async function refreshAuthTokens(
  request: NextRequest,
): Promise<TokenResponse | null> {
  const refreshToken = request.cookies.get(REFRESH_TOKEN_COOKIE)?.value;

  if (!refreshToken || isJwtExpired(refreshToken, 0)) {
    return null;
  }

  const response = await fetch(`${apiBaseUrl}/auth/refresh-token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: "no-store",
  }).catch(() => null);

  if (!response?.ok) {
    return null;
  }

  const tokens = (await response.json().catch(() => null)) as
    | TokenResponse
    | null;

  if (!tokens?.access_token || !tokens.refresh_token) {
    return null;
  }

  return tokens;
}

function setAuthCookies(response: NextResponse, tokens: TokenResponse): void {
  response.cookies.set(
    ACCESS_TOKEN_COOKIE,
    tokens.access_token,
    getAuthCookieOptions(getTokenMaxAgeSeconds(tokens.access_token)),
  );
  response.cookies.set(
    REFRESH_TOKEN_COOKIE,
    tokens.refresh_token,
    getAuthCookieOptions(getTokenMaxAgeSeconds(tokens.refresh_token)),
  );
}

function isPageNavigation(request: NextRequest): boolean {
  return request.method === "GET" || request.method === "HEAD";
}
