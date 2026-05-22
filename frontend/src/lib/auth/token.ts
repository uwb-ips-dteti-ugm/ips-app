export type AccessTokenClaims = {
  user_id: string;
  name: string;
  role_id: string;
  exp?: number;
};

type TokenExpiryClaims = {
  exp?: number;
};

export function decodeJwtPayload<T>(token: string): T | null {
  const [, payload] = token.split(".");
  if (!payload) {
    return null;
  }

  try {
    return JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as T;
  } catch {
    return null;
  }
}

export function isJwtExpired(token: string, skewMs = 30_000): boolean {
  const payload = decodeJwtPayload<TokenExpiryClaims>(token);

  if (!payload?.exp) {
    return true;
  }

  return Date.now() >= payload.exp * 1000 - skewMs;
}

export function getTokenMaxAgeSeconds(token: string): number | undefined {
  const payload = decodeJwtPayload<TokenExpiryClaims>(token);
  if (!payload?.exp) {
    return undefined;
  }

  const maxAge = Math.floor(payload.exp - Date.now() / 1000);
  return maxAge > 0 ? maxAge : undefined;
}
