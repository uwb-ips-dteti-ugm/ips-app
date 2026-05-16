import { cookies } from "next/headers";

import {
  decodeJwtPayload,
  getTokenMaxAgeSeconds,
  isJwtExpired,
  type AccessTokenClaims,
} from "./token";

export const ACCESS_TOKEN_COOKIE = "ips_access_token";
export const REFRESH_TOKEN_COOKIE = "ips_refresh_token";

export type AuthSession = {
  accessToken: string;
  claims: AccessTokenClaims;
};

type BackendTokenResponse = {
  access_token: string;
  refresh_token: string;
};

export async function getAuthSession(): Promise<AuthSession | null> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get(ACCESS_TOKEN_COOKIE)?.value;

  if (!accessToken || isJwtExpired(accessToken)) {
    return null;
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

export async function hasAuthSession(): Promise<boolean> {
  return Boolean(await getAuthSession());
}

export async function setAuthCookies(tokens: BackendTokenResponse): Promise<void> {
  const cookieStore = await cookies();
  const secure = process.env.NODE_ENV === "production";
  const baseCookieOptions = {
    httpOnly: true,
    sameSite: "lax" as const,
    secure,
    path: "/",
  };

  cookieStore.set(ACCESS_TOKEN_COOKIE, tokens.access_token, {
    ...baseCookieOptions,
    maxAge: getTokenMaxAgeSeconds(tokens.access_token),
  });
  cookieStore.set(REFRESH_TOKEN_COOKIE, tokens.refresh_token, {
    ...baseCookieOptions,
    maxAge: getTokenMaxAgeSeconds(tokens.refresh_token),
  });
}

export async function clearAuthCookies(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(ACCESS_TOKEN_COOKIE);
  cookieStore.delete(REFRESH_TOKEN_COOKIE);
}
