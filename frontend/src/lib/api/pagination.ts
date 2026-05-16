import { redirect } from "next/navigation";

import { apiBaseUrl, getAuthHeaders } from "@/lib/api/client";

export type PaginationMeta = {
  page: number;
  limit: number;
  total: number;
};

export type PaginatedResponse<T> = {
  data: T[];
  meta: PaginationMeta;
};

export async function fetchPaginated<T>({
  accessToken,
  path,
  page,
  limit,
  search,
}: {
  accessToken: string;
  path: string;
  page: number;
  limit: number;
  search: string;
}): Promise<PaginatedResponse<T>> {
  const url = new URL(path, apiBaseUrl);
  url.searchParams.set("page", String(page));
  url.searchParams.set("limit", String(limit));

  if (search) {
    url.searchParams.set("search", search);
  }

  const response = await fetch(url, {
    headers: getAuthHeaders(accessToken),
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}.`);
  }

  return (await response.json()) as PaginatedResponse<T>;
}
