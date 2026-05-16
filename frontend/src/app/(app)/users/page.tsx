import { redirect } from "next/navigation";

import { DashboardShell } from "@/app/_components/DashboardShell";
import { canAccessFeature } from "@/lib/api/featureAccess";
import { apiBaseUrl, getAuthHeaders } from "@/lib/api/client";
import { getAuthSession } from "@/lib/auth/session";
import { getStringParam } from "@/lib/navigation/searchParams";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import { UsersPageContent } from "./_components/UsersPageContent";
import {
  type UserRoleFilterOption,
  type UserStateFilterValue,
  type UserStatusFilterValue,
} from "./_components/UsersSearchForm";
import { type UserListItem } from "./_components/UsersTable";

type UsersPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

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

export default async function UsersPage({ searchParams }: UsersPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const resolvedSearchParams = await searchParams;
  const page = getPage(resolvedSearchParams.page);
  const limit = getLimit(resolvedSearchParams.limit);
  const search = getStringParam(resolvedSearchParams.search);
  const roleId = getStringParam(resolvedSearchParams.role_id);
  const state = getUserStateFilter(resolvedSearchParams.state);
  const status = getUserStatusFilter(resolvedSearchParams.status);

  const [
    canViewUsers,
    canManageUsers,
    canDeleteUsers,
    canViewRoles,
    canRegisterUsers,
  ] =
    await Promise.all([
      canAccessFeature(session.accessToken, "user/view"),
      canAccessFeature(session.accessToken, "user/manage"),
      canAccessFeature(session.accessToken, "user/delete"),
      canAccessFeature(session.accessToken, "role/view"),
      canAccessFeature(session.accessToken, "auth/manage"),
    ]);

  if (!canViewUsers) {
    return (
      <DashboardShell session={session}>
        <AccessDenied message="Your account does not have access to view users." />
      </DashboardShell>
    );
  }

  const [users, roles] = await Promise.all([
    getUsers({
      accessToken: session.accessToken,
      page,
      limit,
      search,
      roleId,
      state,
      status,
    }),
    canViewRoles ? getRoles(session.accessToken) : [],
  ]);

  return (
    <DashboardShell session={session}>
      <PageContent>
        <PageHeader title="Users" subtitle="View and manage users." />

        <UsersPageContent
          key={`${users.meta.page}:${users.meta.limit}:${users.meta.total}:${search}:${roleId}:${state}:${status}`}
          users={users.data}
          meta={users.meta}
          filters={{
            search,
            roleId,
            state,
            status,
          }}
          roles={roles}
          canRegisterUsers={canRegisterUsers}
          canManageUsers={canManageUsers}
          canDeleteUsers={canDeleteUsers}
        />
      </PageContent>
    </DashboardShell>
  );
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

  const response = await fetch(url, {
    headers: getAuthHeaders(accessToken),
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

  if (!response.ok) {
    throw new Error("Failed to fetch users.");
  }

  return (await response.json()) as UsersResponse;
}

async function getRoles(accessToken: string): Promise<UserRoleFilterOption[]> {
  const url = new URL("/roles", apiBaseUrl);
  url.searchParams.set("page", "0");
  url.searchParams.set("limit", "100");

  const response = await fetch(url, {
    headers: getAuthHeaders(accessToken),
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

  if (!response.ok) {
    return [];
  }

  const roles = (await response.json()) as RolesResponse;
  return roles.data.map((role) => ({
    id: role.id,
    name: role.name,
  }));
}

function getPage(value: string | string[] | undefined) {
  const page = Number.parseInt(getStringParam(value), 10);
  return Number.isFinite(page) && page >= 0 ? page : 0;
}

function getLimit(value: string | string[] | undefined) {
  const limit = Number.parseInt(getStringParam(value), 10);
  return [10, 20, 50].includes(limit) ? limit : 10;
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
