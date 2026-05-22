export const ACCESS_TOKEN_COOKIE = "ips_access_token";
export const REFRESH_TOKEN_COOKIE = "ips_refresh_token";

export function getAuthCookieOptions(maxAge?: number) {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    ...(maxAge === undefined ? {} : { maxAge }),
  };
}
