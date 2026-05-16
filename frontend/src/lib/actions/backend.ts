import { redirect } from "next/navigation";

import { apiBaseUrl, getAuthHeaders } from "@/lib/api/client";
import { getAuthSession } from "@/lib/auth/session";

export async function getActionAccessToken(): Promise<string> {
  const session = await getAuthSession();

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
  const response = await fetch(new URL(path, apiBaseUrl), {
    ...init,
    headers: {
      ...getAuthHeaders(accessToken),
      ...init.headers,
    },
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

  return response;
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
