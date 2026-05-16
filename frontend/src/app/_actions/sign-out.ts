"use server";

import { redirect } from "next/navigation";

import { clearAuthCookies, getAuthSession } from "@/lib/auth/session";
import { apiBaseUrl, getAuthHeaders } from "@/lib/api/client";

export async function signOutAction(): Promise<void> {
  const session = await getAuthSession();

  if (session) {
    await fetch(`${apiBaseUrl}/auth/sign-out`, {
      method: "POST",
      headers: getAuthHeaders(session.accessToken),
      cache: "no-store",
    }).catch(() => undefined);
  }

  await clearAuthCookies();
  redirect("/sign-in");
}
