import type { UserStatus } from "@/lib/api/user";

export const USER_LIMIT_OPTIONS = [10, 20, 50] as const;

export type UserStatusFilter = "" | UserStatus;

export type UsersListFilters = {
  limit: number;
  roleId: string;
  search: string;
  status: UserStatusFilter;
};

export type UsersListState = UsersListFilters & {
  page: number;
};

export type UsersPageSearchParams = Record<
  string,
  string | string[] | undefined
>;

export function parseUsersListState(
  searchParams: UsersPageSearchParams,
): UsersListState {
  return {
    limit: getLimit(searchParams.limit),
    page: getPage(searchParams.page),
    roleId: getSearchParam(searchParams.role_id),
    search: getSearchParam(searchParams.search).trim(),
    status: getStatus(searchParams.status),
  };
}

export function getUsersListKey(state: UsersListState): string {
  return [
    String(state.page),
    String(state.limit),
    state.roleId,
    state.search,
    state.status,
  ].join(":");
}

export function writeUsersListFilters(
  searchParams: URLSearchParams,
  filters: UsersListFilters,
) {
  setOptionalParam(searchParams, "search", filters.search.trim());
  setOptionalParam(searchParams, "role_id", filters.roleId);
  setOptionalParam(searchParams, "status", filters.status);
  searchParams.set("limit", String(filters.limit));
  searchParams.delete("page");
}

export function writeNextUsersPage(
  searchParams: URLSearchParams,
  page: number,
) {
  searchParams.set("page", String(page + 1));
}

export function writePreviousUsersPage(
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

function getLimit(value: string | string[] | undefined): number {
  const limit = Number.parseInt(getSearchParam(value), 10);

  return USER_LIMIT_OPTIONS.includes(
    limit as (typeof USER_LIMIT_OPTIONS)[number],
  )
    ? limit
    : USER_LIMIT_OPTIONS[0];
}

function getPage(value: string | string[] | undefined): number {
  const page = Number.parseInt(getSearchParam(value), 10);
  return Number.isFinite(page) && page > 0 ? page : 0;
}

function getStatus(value: string | string[] | undefined): UserStatusFilter {
  const status = getSearchParam(value);
  return ["active", "suspended", "banned"].includes(status)
    ? (status as UserStatus)
    : "";
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
