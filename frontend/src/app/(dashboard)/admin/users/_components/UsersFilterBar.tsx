"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { FilterBar } from "@/shared/components/FilterBar";
import { SelectField, TextField } from "@/shared/components/FormControls";

import type { UserRoleFilterOption } from "../_lib/get-users-page-data";
import {
  USER_LIMIT_OPTIONS,
  type UsersListFilters,
  writeUsersListFilters,
} from "../_lib/users-list-state";
import { useListNavigation } from "../../_hooks/use-list-navigation";

const SEARCH_DEBOUNCE_MS = 400;

type UsersFilterBarProps = {
  actions?: ReactNode;
  filters: UsersListFilters;
  onTableLoadingChange: (isLoading: boolean) => void;
  roles: UserRoleFilterOption[];
};

export function UsersFilterBar({
  actions,
  filters,
  onTableLoadingChange,
  roles,
}: UsersFilterBarProps) {
  const [searchValue, setSearchValue] = useState(filters.search);
  const { replaceQuery } = useListNavigation(onTableLoadingChange);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      const search = searchValue.trim();
      if (search === filters.search) {
        return;
      }

      replaceQuery((searchParams) => {
        writeUsersListFilters(searchParams, {
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
        id="users-search"
        label="Search"
        name="search"
        type="search"
        value={searchValue}
        onChange={(event) => setSearchValue(event.currentTarget.value)}
        placeholder="Search user names"
        className="min-w-[220px] flex-1"
        inputClassName="w-full"
      />

      <SelectField
        id="users-role"
        label="Role"
        name="role_id"
        value={filters.roleId}
        onChange={(event) =>
          replaceFilters(replaceQuery, {
            ...filters,
            roleId: event.currentTarget.value,
          })
        }
        className="min-w-[180px] basis-56"
      >
        <option value="">All roles</option>
        {roles.map((role) => (
          <option key={role.id} value={role.id}>
            {role.name}
          </option>
        ))}
      </SelectField>

      <SelectField
        id="users-status"
        label="Status"
        name="status"
        value={filters.status}
        onChange={(event) =>
          replaceFilters(replaceQuery, {
            ...filters,
            status: event.currentTarget.value as UsersListFilters["status"],
          })
        }
        className="min-w-[140px] basis-40"
      >
        <option value="">All statuses</option>
        <option value="active">Active</option>
        <option value="suspended">Suspended</option>
        <option value="banned">Banned</option>
      </SelectField>

      <SelectField
        id="users-limit"
        label="Entries"
        name="limit"
        value={String(filters.limit)}
        onChange={(event) =>
          replaceFilters(replaceQuery, {
            ...filters,
            limit: Number.parseInt(event.currentTarget.value, 10),
          })
        }
        className="w-24"
      >
        {USER_LIMIT_OPTIONS.map((limit) => (
          <option key={limit} value={limit}>
            {limit}
          </option>
        ))}
      </SelectField>

      {actions ? <div className="ml-auto self-end">{actions}</div> : null}
    </FilterBar>
  );
}

function replaceFilters(
  replaceQuery: ReturnType<typeof useListNavigation>["replaceQuery"],
  filters: UsersListFilters,
) {
  replaceQuery((searchParams) => {
    writeUsersListFilters(searchParams, filters);
  });
}
