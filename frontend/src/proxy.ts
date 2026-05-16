import { NextResponse, type NextRequest } from "next/server";

import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/session";
import { isJwtExpired } from "@/lib/auth/token";

const signInPath = "/sign-in";

export function proxy(request: NextRequest) {
  const { nextUrl } = request;
  const accessToken = request.cookies.get(ACCESS_TOKEN_COOKIE)?.value;
  const isSignedIn = Boolean(accessToken && !isJwtExpired(accessToken));

  if (nextUrl.pathname === "/") {
    if (!isSignedIn) {
      return NextResponse.redirect(new URL(signInPath, nextUrl));
    }

    return NextResponse.next();
  }

  if (nextUrl.pathname === signInPath && isSignedIn) {
    return NextResponse.redirect(new URL("/", nextUrl));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/sign-in"],
};
