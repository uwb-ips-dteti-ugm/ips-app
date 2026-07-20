import type { NodeStatus } from "@/lib/api/node";

import { LIST_LIMIT_OPTIONS } from "../../../admin/_lib/page-list-state";

const MAX_UWB_VALUE = 0xffff;

export type NodeStatusFilter = "" | NodeStatus;
export type NodeOnlineFilter = "" | "false" | "true";

export type NodesListFilters = {
  address: string;
  isOnline: NodeOnlineFilter;
  limit: number;
  networkId: string;
  search: string;
  status: NodeStatusFilter;
};

export type NodesListState = NodesListFilters & {
  page: number;
};

export type NodesPageSearchParams = Record<
  string,
  string | string[] | undefined
>;

export function parseNodesListState(
  searchParams: NodesPageSearchParams,
): NodesListState {
  return {
    address: getAddress(searchParams.address),
    isOnline: getOnline(searchParams.is_online),
    limit: getLimit(searchParams.limit),
    networkId: getSearchParam(searchParams.network_id),
    page: getPage(searchParams.page),
    search: getSearchParam(searchParams.search).trim(),
    status: getStatus(searchParams.status),
  };
}

export function getNodesListKey(state: NodesListState): string {
  return [
    state.address,
    state.isOnline,
    String(state.limit),
    state.networkId,
    String(state.page),
    state.search,
    state.status,
  ].join(":");
}

export function writeNodesListFilters(
  searchParams: URLSearchParams,
  filters: NodesListFilters,
) {
  setOptionalParam(searchParams, "address", filters.address);
  setOptionalParam(searchParams, "is_online", filters.isOnline);
  setOptionalParam(searchParams, "network_id", filters.networkId);
  setOptionalParam(searchParams, "search", filters.search.trim());
  setOptionalParam(searchParams, "status", filters.status);
  searchParams.set("limit", String(filters.limit));
  searchParams.delete("page");
}

export function writeNextNodesPage(
  searchParams: URLSearchParams,
  page: number,
) {
  searchParams.set("page", String(page + 1));
}

export function writePreviousNodesPage(
  searchParams: URLSearchParams,
  page: number,
) {
  const previousPage = Math.max(0, page - 1);
  setOptionalParam(
    searchParams,
    "page",
    previousPage ? String(previousPage) : "",
  );
}

export function parseAddressFilter(value: string): string | null {
  const trimmedValue = value.trim();
  if (!trimmedValue) {
    return "";
  }

  const address = Number(trimmedValue);
  if (
    !Number.isInteger(address) ||
    address < 0 ||
    address > MAX_UWB_VALUE
  ) {
    return null;
  }

  return String(address);
}

function getAddress(value: string | string[] | undefined): string {
  return parseAddressFilter(getSearchParam(value)) ?? "";
}

function getLimit(value: string | string[] | undefined): number {
  const limit = Number.parseInt(getSearchParam(value), 10);

  return LIST_LIMIT_OPTIONS.includes(limit as (typeof LIST_LIMIT_OPTIONS)[number])
    ? limit
    : LIST_LIMIT_OPTIONS[0];
}

function getPage(value: string | string[] | undefined): number {
  const page = Number.parseInt(getSearchParam(value), 10);
  return Number.isFinite(page) && page > 0 ? page : 0;
}

function getStatus(value: string | string[] | undefined): NodeStatusFilter {
  const status = getSearchParam(value);
  return ["pending", "approved", "suspended"].includes(status)
    ? (status as NodeStatus)
    : "";
}

function getOnline(value: string | string[] | undefined): NodeOnlineFilter {
  const isOnline = getSearchParam(value);
  return isOnline === "true" || isOnline === "false" ? isOnline : "";
}

function getSearchParam(value: string | string[] | undefined): string {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

function setOptionalParam(
  searchParams: URLSearchParams,
  name: string,
  value: string,
) {
  if (value) {
    searchParams.set(name, value);
  } else {
    searchParams.delete(name);
  }
}
