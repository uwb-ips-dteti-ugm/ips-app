import { NextResponse, type NextRequest } from "next/server";

import {
  ACCESS_TOKEN_COOKIE,
  getAuthCookieOptions,
  REFRESH_TOKEN_COOKIE,
} from "@/lib/auth/cookies";
import { getTokenMaxAgeSeconds, isJwtExpired } from "@/lib/auth/token";
import { env } from "@/lib/env";

const signInPath = "/sign-in";

type TokenResponse = {
  access_token: string;
  refresh_token: string;
};

export async function proxy(request: NextRequest) {
  const { nextUrl } = request;
  const isSignInPath = nextUrl.pathname === signInPath;
  const isNavigation = isPageNavigation(request);

  const accessToken = request.cookies.get(ACCESS_TOKEN_COOKIE)?.value;
  const hasAccessToken = Boolean(accessToken && !isJwtExpired(accessToken));

  if (hasAccessToken) {
    if (isSignInPath && isNavigation) {
      return NextResponse.redirect(new URL("/", nextUrl));
    }

    return NextResponse.next();
  }

  const refreshedTokens = await refreshAuthTokens(request);
  if (refreshedTokens) {
    if (isNavigation) {
      // GET/HEAD: safe to redirect back to the same URL — the browser transparently
      // re-fetches it with the newly-set cookies attached.
      const redirectUrl = isSignInPath ? new URL("/", nextUrl) : nextUrl.clone();
      const response = NextResponse.redirect(redirectUrl);
      setAuthCookies(response, refreshedTokens);
      return response;
    }

    // POST (Server Actions, e.g. the range-monitor/nodes auto-refresh actions and
    // every mutation form): redirecting would drop the action's payload and the
    // mutation would silently never run. Forward the SAME request instead, with the
    // refreshed access token already visible to the downstream Server Action's
    // getAuthSession() call, and persist the rotated tokens on the response too.
    request.cookies.set(ACCESS_TOKEN_COOKIE, refreshedTokens.access_token);
    request.cookies.set(REFRESH_TOKEN_COOKIE, refreshedTokens.refresh_token);
    const response = NextResponse.next({ request });
    setAuthCookies(response, refreshedTokens);
    return response;
  }

  if (isSignInPath) {
    return NextResponse.next();
  }

  // No valid access token and the refresh failed (or there was no refresh token to
  // try) — redirect to sign-in. Next.js honors a redirect response for Server Action
  // invocations the same way it does for page navigations, so this also correctly
  // bounces polling/mutation Server Actions (e.g. range-monitor's auto-refresh) to
  // sign-in instead of leaving them stuck retrying forever.
  const signInUrl = new URL(signInPath, nextUrl);
  signInUrl.searchParams.set(
    "callbackUrl",
    nextUrl.pathname + nextUrl.search,
  );
  const response = NextResponse.redirect(signInUrl);
  response.cookies.delete(ACCESS_TOKEN_COOKIE);
  response.cookies.delete(REFRESH_TOKEN_COOKIE);
  return response;
}

export const config = {
  matcher: ["/", "/admin/:path*", "/node/:path*", "/sign-in"],
};

async function refreshAuthTokens(
  request: NextRequest,
): Promise<TokenResponse | null> {
  const refreshToken = request.cookies.get(REFRESH_TOKEN_COOKIE)?.value;

  if (!refreshToken || isJwtExpired(refreshToken, 0)) {
    return null;
  }

  const response = await fetch(`${env.apiBaseUrl}/auth/refresh-token`, {
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
