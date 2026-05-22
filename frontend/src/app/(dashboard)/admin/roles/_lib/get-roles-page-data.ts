import { getPermissions, type PermissionResponse } from "@/lib/api/permission";
import { getRoles, type RolesResponse } from "@/lib/api/role";
import { getMyPermissions } from "@/lib/api/user";

import type { CursorListState } from "../../_lib/cursor-list-state";

export type RolesPageData = {
  canDeleteRoles: boolean;
  canManageRoles: boolean;
  canViewPermissions: boolean;
  canViewRoles: boolean;
  permissions: PermissionResponse[];
  roles: RolesResponse;
};

export async function getRolesPageData(
  accessToken: string,
  state: CursorListState,
): Promise<RolesPageData> {
  const permissionNames = await readPermissionNames(accessToken);
  const canDeleteRoles = permissionNames.has("role/delete");
  const canManageRoles = permissionNames.has("role/manage");
  const canViewPermissions = permissionNames.has("permission/view");
  const canViewRoles = permissionNames.has("role/view");

  if (!canViewRoles) {
    return {
      canDeleteRoles,
      canManageRoles,
      canViewPermissions,
      canViewRoles,
      permissions: [],
      roles: emptyRoles(state.limit),
    };
  }

  const [roles, permissions] = await Promise.all([
    getRoles(
      {
        cursor_id: optionalQueryValue(state.cursorId),
        limit: state.limit,
        page: 0,
        search: optionalQueryValue(state.search),
      },
      { accessToken },
    ),
    canViewPermissions ? readPermissions(accessToken) : [],
  ]);

  return {
    canDeleteRoles,
    canManageRoles,
    canViewPermissions,
    canViewRoles,
    permissions,
    roles,
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

async function readPermissions(
  accessToken: string,
): Promise<PermissionResponse[]> {
  try {
    const permissions = await getPermissions(
      { limit: 500, page: 0 },
      { accessToken },
    );
    return permissions.data;
  } catch {
    return [];
  }
}

function emptyRoles(limit: number): RolesResponse {
  return {
    data: [],
    meta: {
      limit,
      page: 0,
      total: 0,
    },
  };
}

function optionalQueryValue(value: string): string | undefined {
  return value || undefined;
}
