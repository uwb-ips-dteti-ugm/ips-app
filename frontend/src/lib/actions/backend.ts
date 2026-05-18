import { redirect } from "next/navigation";

import { apiBaseUrl, authenticatedFetch } from "@/lib/api/client";
import { getAuthSession } from "@/lib/auth/session";

export async function getActionAccessToken(): Promise<string> {
  const session = await getAuthSession({ persistRefresh: true });

  if (!session) {
    redirect("/sign-in");
  }

  return session.accessToken;
}

export async function fetchBackend(
  accessToken: string,
  path: string,
  init: RequestInit,
): Promise<Response> {
  return authenticatedFetch(
    accessToken,
    new URL(path, apiBaseUrl),
    {
      ...init,
      headers: {
        ...init.headers,
      },
    },
    { persistRefresh: true },
  );
}

export async function jsonBackend(
  accessToken: string,
  path: string,
  method: "POST" | "PATCH" | "DELETE",
  body: Record<string, unknown>,
): Promise<Response> {
  return fetchBackend(accessToken, path, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
}
