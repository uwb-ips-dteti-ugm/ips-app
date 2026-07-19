"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { FilterBar } from "@/shared/components/FilterBar";
import { SelectField, TextField } from "@/shared/components/FormControls";

import {
  LIST_LIMIT_OPTIONS,
  type PageListFilters,
  writePageListFilters,
} from "../_lib/page-list-state";
import { useListNavigation } from "../_hooks/use-list-navigation";

const SEARCH_DEBOUNCE_MS = 400;

type ResourceFilterBarProps = {
  actions?: ReactNode;
  filters: PageListFilters;
  onTableLoadingChange: (isLoading: boolean) => void;
  searchLabel: string;
  searchPlaceholder: string;
};

export function ResourceFilterBar({
  actions,
  filters,
  onTableLoadingChange,
  searchLabel,
  searchPlaceholder,
}: ResourceFilterBarProps) {
  const [searchValue, setSearchValue] = useState(filters.search);
  const { replaceQuery } = useListNavigation(onTableLoadingChange);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      const search = searchValue.trim();
      if (search === filters.search) {
        return;
      }

      replaceQuery((searchParams) => {
        writePageListFilters(searchParams, {
          ...filters,
          search,
        });
      });
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timeout);
  }, [filters, replaceQuery, searchValue]);

  return (
    <FilterBar>
      <TextField
        label={searchLabel}
        name="search"
        type="search"
        value={searchValue}
        onChange={(event) => setSearchValue(event.currentTarget.value)}
        placeholder={searchPlaceholder}
        className="min-w-[220px] flex-1"
        inputClassName="w-full"
      />

      <SelectField
        label="Entries"
        name="limit"
        value={String(filters.limit)}
        onChange={(event) =>
          replaceQuery((searchParams) => {
            writePageListFilters(searchParams, {
              ...filters,
              limit: Number.parseInt(event.currentTarget.value, 10),
            });
          })
        }
        className="w-24"
      >
        {LIST_LIMIT_OPTIONS.map((limit) => (
          <option key={limit} value={limit}>
            {limit}
          </option>
        ))}
      </SelectField>

      {actions ? <div className="ml-auto self-end">{actions}</div> : null}
    </FilterBar>
  );
}
