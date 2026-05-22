"use server";

import { redirect } from "next/navigation";

import { clearAuthCookies } from "@/lib/auth/session";

export async function signOutAction(): Promise<void> {
  await clearAuthCookies();
  redirect("/sign-in");
}
