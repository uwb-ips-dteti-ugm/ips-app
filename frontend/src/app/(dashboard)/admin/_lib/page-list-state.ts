export const LIST_LIMIT_OPTIONS = [10, 20, 50] as const;

export type PageListFilters = {
  limit: number;
  search: string;
};

export type PageListState = PageListFilters & {
  page: number;
};

export type PageSearchParams = Record<string, string | string[] | undefined>;

export function parsePageListState(
  searchParams: PageSearchParams,
): PageListState {
  return {
    limit: getLimit(searchParams.limit),
    page: getPage(searchParams.page),
    search: getSearchParam(searchParams.search).trim(),
  };
}

export function getPageListKey(state: PageListState): string {
  return [String(state.page), String(state.limit), state.search].join(":");
}

export function writePageListFilters(
  searchParams: URLSearchParams,
  filters: PageListFilters,
) {
  setOptionalParam(searchParams, "search", filters.search.trim());
  searchParams.set("limit", String(filters.limit));
  searchParams.delete("page");
}

export function writeNextPage(searchParams: URLSearchParams, page: number) {
  searchParams.set("page", String(page + 1));
}

export function writePreviousPage(
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

  return LIST_LIMIT_OPTIONS.includes(limit as (typeof LIST_LIMIT_OPTIONS)[number])
    ? limit
    : LIST_LIMIT_OPTIONS[0];
}

function getPage(value: string | string[] | undefined): number {
  const page = Number.parseInt(getSearchParam(value), 10);
  return Number.isFinite(page) && page > 0 ? page : 0;
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
