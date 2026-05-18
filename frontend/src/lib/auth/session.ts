import { cookies } from "next/headers";

import {
  decodeJwtPayload,
  getTokenMaxAgeSeconds,
  isJwtExpired,
  type AccessTokenClaims,
} from "./token";
import {
  ACCESS_TOKEN_COOKIE,
  getAuthCookieOptions,
  REFRESH_TOKEN_COOKIE,
} from "./cookies";

export { ACCESS_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE } from "./cookies";

export type AuthSession = {
  accessToken: string;
  claims: AccessTokenClaims;
};

type BackendTokenResponse = {
  access_token: string;
  refresh_token: string;
};

const apiBaseUrl =
  process.env.IPS_API_BASE_URL ??
  process.env.NEXT_PUBLIC_IPS_API_BASE_URL ??
  "http://localhost:8000";

export async function getAuthSession({
  persistRefresh = false,
}: {
  persistRefresh?: boolean;
} = {}): Promise<AuthSession | null> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get(ACCESS_TOKEN_COOKIE)?.value;

  if (!accessToken || isJwtExpired(accessToken)) {
    const tokens = await refreshAuthTokens({ persist: persistRefresh });
    if (!tokens) {
      return null;
    }

    const claims = decodeJwtPayload<AccessTokenClaims>(tokens.access_token);
    if (!claims) {
      return null;
    }

    return {
      accessToken: tokens.access_token,
      claims,
    };
  }

  const claims = decodeJwtPayload<AccessTokenClaims>(accessToken);
  if (!claims) {
    return null;
  }

  return {
    accessToken,
    claims,
  };
}

export async function refreshAuthTokens({
  persist = false,
}: {
  persist?: boolean;
} = {}): Promise<BackendTokenResponse | null> {
  const cookieStore = await cookies();
  const refreshToken = cookieStore.get(REFRESH_TOKEN_COOKIE)?.value;

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

  const tokens = (await response.json()) as BackendTokenResponse;
  if (persist) {
    await setAuthCookies(tokens);
  }

  return tokens;
}

export async function hasAuthSession(): Promise<boolean> {
  return Boolean(await getAuthSession());
}

export async function setAuthCookies(tokens: BackendTokenResponse): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(ACCESS_TOKEN_COOKIE, tokens.access_token, {
    ...getAuthCookieOptions(getTokenMaxAgeSeconds(tokens.access_token)),
  });
  cookieStore.set(REFRESH_TOKEN_COOKIE, tokens.refresh_token, {
    ...getAuthCookieOptions(getTokenMaxAgeSeconds(tokens.refresh_token)),
  });
}

export async function clearAuthCookies(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(ACCESS_TOKEN_COOKIE);
  cookieStore.delete(REFRESH_TOKEN_COOKIE);
}
