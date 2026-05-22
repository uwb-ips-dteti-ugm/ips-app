export const LIST_LIMIT_OPTIONS = [10, 20, 50] as const;

export type CursorListFilters = {
  limit: number;
  search: string;
};

export type CursorListState = CursorListFilters & {
  cursorId: string;
  cursorStack: string[];
};

export type PageSearchParams = Record<string, string | string[] | undefined>;

export function parseCursorListState(
  searchParams: PageSearchParams,
): CursorListState {
  return {
    cursorId: getSearchParam(searchParams.cursor_id),
    cursorStack: getSearchParamValues(searchParams.cursor_stack),
    limit: getLimit(searchParams.limit),
    search: getSearchParam(searchParams.search).trim(),
  };
}

export function getCursorListKey(state: CursorListState): string {
  return [
    state.cursorId,
    ...state.cursorStack,
    String(state.limit),
    state.search,
  ].join(":");
}

export function writeCursorListFilters(
  searchParams: URLSearchParams,
  filters: CursorListFilters,
) {
  setOptionalParam(searchParams, "search", filters.search.trim());
  searchParams.set("limit", String(filters.limit));
  searchParams.delete("cursor_id");
  searchParams.delete("cursor_stack");
}

export function writeNextCursor(
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

export function writePreviousCursor(searchParams: URLSearchParams) {
  const cursorStack = readCursorStack(searchParams);
  const previousCursorId = cursorStack.pop();

  setOptionalParam(searchParams, "cursor_id", previousCursorId ?? "");
  writeCursorStack(searchParams, cursorStack);
}

function getLimit(value: string | string[] | undefined): number {
  const limit = Number.parseInt(getSearchParam(value), 10);

  return LIST_LIMIT_OPTIONS.includes(limit as (typeof LIST_LIMIT_OPTIONS)[number])
    ? limit
    : LIST_LIMIT_OPTIONS[0];
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
