"use server";

import { redirect } from "next/navigation";

import { clearAuthCookies, getAuthSession } from "@/lib/auth/session";

const apiBaseUrl =
  process.env.IPS_API_BASE_URL ??
  process.env.NEXT_PUBLIC_IPS_API_BASE_URL ??
  "http://localhost:8000";

export async function signOutAction(): Promise<void> {
  const session = await getAuthSession();

  if (session) {
    await fetch(`${apiBaseUrl}/auth/sign-out`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
      cache: "no-store",
    }).catch(() => undefined);
  }

  await clearAuthCookies();
  redirect("/sign-in");
}
