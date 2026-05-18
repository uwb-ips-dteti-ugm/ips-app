import { redirect } from "next/navigation";

import { apiBaseUrl, getAuthHeaders } from "@/lib/api/client";
import { type PaginatedResponse } from "@/lib/api/pagination";

export type NodeStatus = "pending" | "approved" | "suspended" | "revoked";

export type NodeListItem = {
  id: string;
  device_id: string;
  name: string;
  description: string;
  preferences: Record<string, unknown>;
  status: NodeStatus;
  is_approved: boolean;
  approved_at: string | null;
  approved_by: string | null;
  last_seen_at: string | null;
  last_connected_at: string | null;
  last_disconnected_at: string | null;
  created_at: string;
  created_by: string | null;
  updated_at: string | null;
  updated_by: string | null;
  version: number;
};

type RegisteredNodesResponse = {
  data: string[];
};

export async function fetchNodes({
  accessToken,
  page = 0,
  limit = 100,
  search = "",
  status,
}: {
  accessToken: string;
  page?: number;
  limit?: number;
  search?: string;
  status?: NodeStatus;
}): Promise<PaginatedResponse<NodeListItem>> {
  const url = new URL("/nodes", apiBaseUrl);
  url.searchParams.set("page", String(page));
  url.searchParams.set("limit", String(limit));

  if (search) {
    url.searchParams.set("search", search);
  }
  if (status) {
    url.searchParams.set("status", status);
  }

  const response = await fetch(url, {
    headers: getAuthHeaders(accessToken),
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

  if (!response.ok) {
    throw new Error("Failed to fetch nodes.");
  }

  return (await response.json()) as PaginatedResponse<NodeListItem>;
}

export async function fetchNodeByDeviceId(
  accessToken: string,
  deviceId: string,
): Promise<NodeListItem | null> {
  const response = await fetch(new URL(`/nodes/device/${deviceId}`, apiBaseUrl), {
    headers: getAuthHeaders(accessToken),
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error("Failed to fetch node by device ID.");
  }

  return (await response.json()) as NodeListItem;
}

export async function fetchRegisteredNodeIds(
  accessToken: string,
): Promise<string[]> {
  const response = await fetch(new URL("/nodes/registered", apiBaseUrl), {
    headers: getAuthHeaders(accessToken),
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

  if (!response.ok) {
    return [];
  }

  const body = (await response.json()) as RegisteredNodesResponse;
  return body.data;
}
