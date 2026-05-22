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
  cursorId: string;
  cursorStack: string[];
};

export type UsersPageSearchParams = Record<
  string,
  string | string[] | undefined
>;

export function parseUsersListState(
  searchParams: UsersPageSearchParams,
): UsersListState {
  return {
    cursorId: getSearchParam(searchParams.cursor_id),
    cursorStack: getSearchParamValues(searchParams.cursor_stack),
    limit: getLimit(searchParams.limit),
    roleId: getSearchParam(searchParams.role_id),
    search: getSearchParam(searchParams.search).trim(),
    status: getStatus(searchParams.status),
  };
}

export function getUsersListKey(state: UsersListState): string {
  return [
    state.cursorId,
    ...state.cursorStack,
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
  searchParams.delete("cursor_id");
  searchParams.delete("cursor_stack");
}

export function writeNextUsersCursor(
  searchParams: URLSearchParams,
  nextCursorId: string,
) {
  const currentCursorId = searchParams.get("cursor_id") ?? "";
  const cursorStack = readCursorStack(searchParams);

  if (currentCursorId) {
    cursorStack.push(currentCursorId);
  }

  searchParams.set("cursor_id", nextCursorId);
  writeCursorStack(searchParams, cursorStack);
}

export function writePreviousUsersCursor(searchParams: URLSearchParams) {
  const cursorStack = readCursorStack(searchParams);
  const previousCursorId = cursorStack.pop();

  setOptionalParam(searchParams, "cursor_id", previousCursorId ?? "");
  writeCursorStack(searchParams, cursorStack);
}

function getLimit(value: string | string[] | undefined): number {
  const limit = Number.parseInt(getSearchParam(value), 10);

  return USER_LIMIT_OPTIONS.includes(
    limit as (typeof USER_LIMIT_OPTIONS)[number],
  )
    ? limit
    : USER_LIMIT_OPTIONS[0];
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

function getSearchParamValues(
  value: string | string[] | undefined,
): string[] {
  const values = Array.isArray(value) ? value : value ? [value] : [];
  return values.map((item) => item.trim()).filter(Boolean);
}

function readCursorStack(searchParams: URLSearchParams): string[] {
  return searchParams
    .getAll("cursor_stack")
    .map((cursorId) => cursorId.trim())
    .filter(Boolean);
}

function writeCursorStack(
  searchParams: URLSearchParams,
  cursorStack: string[],
) {
  searchParams.delete("cursor_stack");

  for (const cursorId of cursorStack) {
    searchParams.append("cursor_stack", cursorId);
  }
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
