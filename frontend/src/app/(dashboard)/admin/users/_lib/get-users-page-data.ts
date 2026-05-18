import { apiBaseUrl, authenticatedFetch } from "@/lib/api/client";
import { canAccessFeature } from "@/lib/api/featureAccess";
import { getLimitParam, getPageParam, getStringParam } from "@/lib/navigation/searchParams";

import {
  type UserRoleFilterOption,
  type UserStateFilterValue,
  type UserStatusFilterValue,
} from "../_components/UsersSearchForm";
import { type UserListItem } from "../_components/UsersTable";

export type UsersPageSearchParams = Record<
  string,
  string | string[] | undefined
>;

type UsersResponse = {
  data: UserListItem[];
  meta: {
    page: number;
    limit: number;
    total: number;
  };
};

type RolesResponse = {
  data: UserRoleFilterOption[];
  meta: {
    page: number;
    limit: number;
    total: number;
  };
};

export type UsersPageData = {
  canViewUsers: boolean;
  canManageUsers: boolean;
  canDeleteUsers: boolean;
  canRegisterUsers: boolean;
  users: UsersResponse;
  roles: UserRoleFilterOption[];
  filters: {
    search: string;
    roleId: string;
    state: UserStateFilterValue;
    status: UserStatusFilterValue;
  };
};

export async function getUsersPageData(
  accessToken: string,
  searchParams: UsersPageSearchParams,
): Promise<UsersPageData> {
  const page = getPageParam(searchParams.page);
  const limit = getLimitParam(searchParams.limit);
  const search = getStringParam(searchParams.search);
  const roleId = getStringParam(searchParams.role_id);
  const state = getUserStateFilter(searchParams.state);
  const status = getUserStatusFilter(searchParams.status);

  const [
    canViewUsers,
    canManageUsers,
    canDeleteUsers,
    canViewRoles,
    canRegisterUsers,
  ] = await Promise.all([
    canAccessFeature(accessToken, "user/view"),
    canAccessFeature(accessToken, "user/manage"),
    canAccessFeature(accessToken, "user/delete"),
    canAccessFeature(accessToken, "role/view"),
    canAccessFeature(accessToken, "auth/manage"),
  ]);

  if (!canViewUsers) {
    return {
      canViewUsers,
      canManageUsers,
      canDeleteUsers,
      canRegisterUsers,
      users: {
        data: [],
        meta: { page, limit, total: 0 },
      },
      roles: [],
      filters: {
        search,
        roleId,
        state,
        status,
      },
    };
  }

  const [users, roles] = await Promise.all([
    getUsers({
      accessToken,
      page,
      limit,
      search,
      roleId,
      state,
      status,
    }),
    canViewRoles ? getRoles(accessToken) : [],
  ]);

  return {
    canViewUsers,
    canManageUsers,
    canDeleteUsers,
    canRegisterUsers,
    users,
    roles,
    filters: {
      search,
      roleId,
      state,
      status,
    },
  };
}

async function getUsers({
  accessToken,
  page,
  limit,
  search,
  roleId,
  state,
  status,
}: {
  accessToken: string;
  page: number;
  limit: number;
  search: string;
  roleId: string;
  state: UserStateFilterValue;
  status: UserStatusFilterValue;
}): Promise<UsersResponse> {
  const url = new URL("/users", apiBaseUrl);
  url.searchParams.set("page", String(page));
  url.searchParams.set("limit", String(limit));

  if (search) {
    url.searchParams.set("search", search);
  }

  if (roleId) {
    url.searchParams.set("role_id", roleId);
  }

  if (state) {
    url.searchParams.set("state", state);
  }

  if (status) {
    url.searchParams.set("status", status);
  }

  const response = await authenticatedFetch(accessToken, url);

  if (!response.ok) {
    throw new Error("Failed to fetch users.");
  }

  return (await response.json()) as UsersResponse;
}

async function getRoles(accessToken: string): Promise<UserRoleFilterOption[]> {
  const url = new URL("/roles", apiBaseUrl);
  url.searchParams.set("page", "0");
  url.searchParams.set("limit", "100");

  const response = await authenticatedFetch(accessToken, url);

  if (!response.ok) {
    return [];
  }

  const roles = (await response.json()) as RolesResponse;
  return roles.data.map((role) => ({
    id: role.id,
    name: role.name,
  }));
}

function getUserStateFilter(
  value: string | string[] | undefined,
): UserStateFilterValue {
  const state = getStringParam(value);
  return ["online", "offline", "away", "dnd"].includes(state)
    ? (state as UserStateFilterValue)
    : "";
}

function getUserStatusFilter(
  value: string | string[] | undefined,
): UserStatusFilterValue {
  const status = getStringParam(value);
  return ["active", "suspended", "banned"].includes(status)
    ? (status as UserStatusFilterValue)
    : "";
}
