import type { NodeStatus } from "@/lib/api/node";

import { LIST_LIMIT_OPTIONS } from "../../../admin/_lib/cursor-list-state";

const MAX_UWB_VALUE = 0xffff;

export type NodeStatusFilter = "" | NodeStatus;

export type NodesListFilters = {
  address: string;
  limit: number;
  networkId: string;
  search: string;
  status: NodeStatusFilter;
};

export type NodesListState = NodesListFilters & {
  cursorId: string;
  cursorStack: string[];
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
    cursorId: getSearchParam(searchParams.cursor_id),
    cursorStack: getSearchParamValues(searchParams.cursor_stack),
    limit: getLimit(searchParams.limit),
    networkId: getSearchParam(searchParams.network_id),
    search: getSearchParam(searchParams.search).trim(),
    status: getStatus(searchParams.status),
  };
}

export function getNodesListKey(state: NodesListState): string {
  return [
    state.address,
    state.cursorId,
    ...state.cursorStack,
    String(state.limit),
    state.networkId,
    state.search,
    state.status,
  ].join(":");
}

export function writeNodesListFilters(
  searchParams: URLSearchParams,
  filters: NodesListFilters,
) {
  setOptionalParam(searchParams, "address", filters.address);
  setOptionalParam(searchParams, "network_id", filters.networkId);
  setOptionalParam(searchParams, "search", filters.search.trim());
  setOptionalParam(searchParams, "status", filters.status);
  searchParams.set("limit", String(filters.limit));
  searchParams.delete("cursor_id");
  searchParams.delete("cursor_stack");
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

function getStatus(value: string | string[] | undefined): NodeStatusFilter {
  const status = getSearchParam(value);
  return ["pending", "approved", "suspended", "revoked"].includes(status)
    ? (status as NodeStatus)
    : "";
}

function getSearchParam(value: string | string[] | undefined): string {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

function getSearchParamValues(
  value: string | string[] | undefined,
): string[] {
  const values = Array.isArray(value) ? value : value ? [value] : [];
  return values.map((item) => item.trim()).filter(Boolean);
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
