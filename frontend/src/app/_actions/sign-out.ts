"use server";

import { redirect } from "next/navigation";

import { clearAuthCookies, getAuthSession } from "@/lib/auth/session";
import { apiBaseUrl, authenticatedFetch } from "@/lib/api/client";

export async function signOutAction(): Promise<void> {
  const session = await getAuthSession({ persistRefresh: true });

  if (session) {
    await authenticatedFetch(
      session.accessToken,
      new URL("/auth/sign-out", apiBaseUrl),
      { method: "POST" },
      { persistRefresh: true, redirectOnUnauthorized: false },
    ).catch(() => undefined);
  }

  await clearAuthCookies();
  redirect("/sign-in");
}
