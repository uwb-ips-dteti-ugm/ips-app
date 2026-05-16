"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, useTransition } from "react";

import { FilterBar } from "@/shared/components/FilterBar";
import { SelectField, TextField } from "@/shared/components/FormControls";

const SEARCH_DEBOUNCE_MS = 400;

type UsersSearchFormProps = {
  search: string;
  limit: number;
  roleId: string;
  state: UserStateFilterValue;
  status: UserStatusFilterValue;
  roles: UserRoleFilterOption[];
  canRegisterUsers: boolean;
  onRegisterUser: () => void;
  onTableLoadingChange: (isLoading: boolean) => void;
};

export type UserStateFilterValue = "" | "online" | "offline" | "away" | "dnd";
export type UserStatusFilterValue = "" | "active" | "suspended" | "banned";

export type UserRoleFilterOption = {
  id: string;
  name: string;
};

export function UsersSearchForm({
  search,
  limit,
  roleId,
  state,
  status,
  roles,
  canRegisterUsers,
  onRegisterUser,
  onTableLoadingChange,
}: UsersSearchFormProps) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [searchValue, setSearchValue] = useState(search);
  const [, startTransition] = useTransition();

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      const normalizedSearch = searchValue.trim();
      const currentSearch = searchParams.get("search") ?? "";

      if (normalizedSearch === currentSearch) {
        return;
      }

      replaceUsersQuery({
        pathname,
        router,
        searchParams,
        search: normalizedSearch,
        limit,
        roleId,
        state,
        status,
        onTableLoadingChange,
        startTransition,
      });
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timeout);
  }, [
    limit,
    pathname,
    roleId,
    onTableLoadingChange,
    router,
    searchParams,
    searchValue,
    startTransition,
    state,
    status,
  ]);

  return (
    <FilterBar>
      <TextField
        id="users-search"
        label="Search"
        name="search"
        type="search"
        value={searchValue}
        onChange={(event) => {
          const nextSearch = event.currentTarget.value;
          setSearchValue(nextSearch);
          onTableLoadingChange(
            nextSearch.trim() !== (searchParams.get("search") ?? ""),
          );
        }}
        placeholder="Search users"
        className="min-w-[220px] flex-1"
        inputClassName="w-full min-w-0"
      />

      <SelectField
        id="users-role"
        label="Role"
        name="role_id"
        value={roleId}
        onChange={(event) =>
          replaceUsersQuery({
            pathname,
            router,
            searchParams,
            search: searchValue.trim(),
            limit,
            roleId: event.currentTarget.value,
            state,
            status,
            onTableLoadingChange,
            startTransition,
          })
        }
        className="min-w-[180px] basis-56"
      >
        <option value="">all</option>
        {roles.map((role) => (
          <option key={role.id} value={role.id}>
            {role.name}
          </option>
        ))}
      </SelectField>

      <SelectField
        id="users-state"
        label="State"
        name="state"
        value={state}
        onChange={(event) =>
          replaceUsersQuery({
            pathname,
            router,
            searchParams,
            search: searchValue.trim(),
            limit,
            roleId,
            state: event.currentTarget.value as UserStateFilterValue,
            status,
            onTableLoadingChange,
            startTransition,
          })
        }
        className="min-w-[140px] basis-40"
      >
        <option value="">all</option>
        <option value="online">online</option>
        <option value="offline">offline</option>
        <option value="away">away</option>
        <option value="dnd">dnd</option>
      </SelectField>

      <SelectField
        id="users-status"
        label="Status"
        name="status"
        value={status}
        onChange={(event) =>
          replaceUsersQuery({
            pathname,
            router,
            searchParams,
            search: searchValue.trim(),
            limit,
            roleId,
            state,
            status: event.currentTarget.value as UserStatusFilterValue,
            onTableLoadingChange,
            startTransition,
          })
        }
        className="min-w-[140px] basis-40"
      >
        <option value="">all</option>
        <option value="active">active</option>
        <option value="suspended">suspended</option>
        <option value="banned">banned</option>
      </SelectField>

      <SelectField
        id="users-limit"
        label="Entries"
        name="limit"
        value={String(limit)}
        onChange={(event) =>
          replaceUsersQuery({
            pathname,
            router,
            searchParams,
            search: searchValue.trim(),
            limit: Number.parseInt(event.currentTarget.value, 10),
            roleId,
            state,
            status,
            onTableLoadingChange,
            startTransition,
          })
        }
        className="w-24"
      >
        <option value="10">10</option>
        <option value="20">20</option>
        <option value="50">50</option>
      </SelectField>

      {canRegisterUsers && (
        <button
          type="button"
          onClick={onRegisterUser}
          className="ml-auto flex h-10 items-center justify-center self-end whitespace-nowrap rounded-md bg-[#0F2854] px-4 text-sm font-semibold text-white transition hover:bg-[#1C4D8D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] dark:bg-[#4988C4] dark:hover:bg-[#1C4D8D]"
        >
          + Register
        </button>
      )}
    </FilterBar>
  );
}

function replaceUsersQuery({
  pathname,
  router,
  searchParams,
  search,
  limit,
  roleId,
  state,
  status,
  onTableLoadingChange,
  startTransition,
}: {
  pathname: string;
  router: ReturnType<typeof useRouter>;
  searchParams: ReturnType<typeof useSearchParams>;
  search: string;
  limit: number;
  roleId: string;
  state: UserStateFilterValue;
  status: UserStatusFilterValue;
  onTableLoadingChange: (isLoading: boolean) => void;
  startTransition: (callback: () => void) => void;
}) {
  const nextSearchParams = new URLSearchParams(searchParams.toString());
  nextSearchParams.set("page", "0");
  nextSearchParams.set("limit", String(limit));

  if (search) {
    nextSearchParams.set("search", search);
  } else {
    nextSearchParams.delete("search");
  }

  if (roleId) {
    nextSearchParams.set("role_id", roleId);
  } else {
    nextSearchParams.delete("role_id");
  }

  if (state) {
    nextSearchParams.set("state", state);
  } else {
    nextSearchParams.delete("state");
  }

  if (status) {
    nextSearchParams.set("status", status);
  } else {
    nextSearchParams.delete("status");
  }

  const nextQuery = nextSearchParams.toString();
  const currentQuery = searchParams.toString();

  if (nextQuery === currentQuery) {
    onTableLoadingChange(false);
    return;
  }

  onTableLoadingChange(true);
  startTransition(() => {
    router.replace(`${pathname}?${nextQuery}`, { scroll: false });
  });
}
