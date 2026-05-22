import { cookies } from "next/headers";

import type { TokenResponse } from "@/lib/api/auth";

import {
  ACCESS_TOKEN_COOKIE,
  getAuthCookieOptions,
  REFRESH_TOKEN_COOKIE,
} from "./cookies";
import {
  decodeJwtPayload,
  getTokenMaxAgeSeconds,
  isJwtExpired,
  type AccessTokenClaims,
} from "./token";

export type AuthSession = {
  accessToken: string;
  claims: AccessTokenClaims;
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

export async function setAuthCookies(tokens: TokenResponse): Promise<void> {
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
