import { getRoles } from "@/lib/api/role";
import {
  getMyPermissions,
  getUsers,
  type UserResponse,
  type UsersResponse,
} from "@/lib/api/user";

import type { UsersListState } from "./users-list-state";

export type UserRoleFilterOption = {
  id: string;
  name: string;
};

export type UsersPageData = {
  canDeleteUsers: boolean;
  canManageUsers: boolean;
  canRegisterUsers: boolean;
  canResetUserPasswords: boolean;
  canViewUsers: boolean;
  roles: UserRoleFilterOption[];
  users: UsersResponse;
};

export async function getUsersPageData(
  accessToken: string,
  state: UsersListState,
): Promise<UsersPageData> {
  const permissionNames = await readPermissionNames(accessToken);
  const canDeleteUsers = permissionNames.has("user/delete");
  const canManageUsers = permissionNames.has("user/manage");
  const canRegisterUsers = permissionNames.has("auth/manage");
  const canResetUserPasswords = permissionNames.has("auth/manage");
  const canViewUsers = permissionNames.has("user/view");

  if (!canViewUsers) {
    return {
      canDeleteUsers,
      canManageUsers,
      canRegisterUsers,
      canResetUserPasswords,
      canViewUsers,
      roles: [],
      users: emptyUsers(state.page, state.limit),
    };
  }

  const [users, roles] = await Promise.all([
    getUsers(
      {
        limit: state.limit,
        page: state.page,
        role_id: optionalQueryValue(state.roleId),
        search: optionalQueryValue(state.search),
        status: state.status || undefined,
      },
      { accessToken },
    ),
    permissionNames.has("role/view") ? readRoleOptions(accessToken) : [],
  ]);

  return {
    canDeleteUsers,
    canManageUsers,
    canRegisterUsers,
    canResetUserPasswords,
    canViewUsers,
    roles,
    users,
  };
}

async function readPermissionNames(accessToken: string): Promise<Set<string>> {
  try {
    const permissions = await getMyPermissions({ accessToken });
    return new Set(permissions.map((permission) => permission.name));
  } catch {
    return new Set();
  }
}

async function readRoleOptions(
  accessToken: string,
): Promise<UserRoleFilterOption[]> {
  try {
    const roles = await getRoles({ limit: 100, page: 0 }, { accessToken });
    return roles.items.map((role) => ({
      id: role.id,
      name: role.name,
    }));
  } catch {
    return [];
  }
}

function emptyUsers(page: number, limit: number): UsersResponse {
  return {
    items: [] satisfies UserResponse[],
    limit,
    page,
    total: 0,
  };
}

function optionalQueryValue(value: string): string | undefined {
  return value || undefined;
}
