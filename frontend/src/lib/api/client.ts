import { redirect } from "next/navigation";

import { refreshAuthTokens } from "@/lib/auth/session";

export const apiBaseUrl =
  process.env.IPS_API_BASE_URL ??
  process.env.NEXT_PUBLIC_IPS_API_BASE_URL ??
  "http://localhost:8000";

export function getAuthHeaders(accessToken: string): HeadersInit {
  return {
    Authorization: `Bearer ${accessToken}`,
  };
}

type AuthenticatedFetchOptions = {
  persistRefresh?: boolean;
  redirectOnUnauthorized?: boolean;
};

export async function authenticatedFetch(
  accessToken: string,
  input: string | URL,
  init: RequestInit = {},
  {
    persistRefresh = false,
    redirectOnUnauthorized = true,
  }: AuthenticatedFetchOptions = {},
): Promise<Response> {
  const response = await fetchWithAccessToken(accessToken, input, init);

  if (response.status !== 401) {
    return response;
  }

  const refreshedTokens = await refreshAuthTokens({ persist: persistRefresh });
  if (!refreshedTokens) {
    if (redirectOnUnauthorized) {
      redirect("/sign-in");
    }
    return response;
  }

  const retryResponse = await fetchWithAccessToken(
    refreshedTokens.access_token,
    input,
    init,
  );
  if (retryResponse.status === 401 && redirectOnUnauthorized) {
    redirect("/sign-in");
  }

  return retryResponse;
}

function fetchWithAccessToken(
  accessToken: string,
  input: string | URL,
  init: RequestInit,
): Promise<Response> {
  return fetch(input, {
    ...init,
    headers: {
      ...getAuthHeaders(accessToken),
      ...init.headers,
    },
    cache: "no-store",
  });
}
