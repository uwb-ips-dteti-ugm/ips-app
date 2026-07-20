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
    return JSON.parse(decodeBase64Url(payload)) as T;
  } catch {
    return null;
  }
}

// Uses atob() instead of Buffer so this module works in both the Node.js and Edge
// runtimes (Buffer isn't available in Edge middleware).
function decodeBase64Url(value: string): string {
  const base64 = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");
  const binary = atob(padded);
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  return new TextDecoder().decode(bytes);
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
