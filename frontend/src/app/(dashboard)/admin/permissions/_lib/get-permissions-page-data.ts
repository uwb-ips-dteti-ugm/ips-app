import { getPermissions, type PermissionsResponse } from "@/lib/api/permission";
import { getMyPermissions } from "@/lib/api/user";

import type { CursorListState } from "../../_lib/cursor-list-state";

export type PermissionsPageData = {
  canDeletePermissions: boolean;
  canManagePermissions: boolean;
  canViewPermissions: boolean;
  permissions: PermissionsResponse;
};

export async function getPermissionsPageData(
  accessToken: string,
  state: CursorListState,
): Promise<PermissionsPageData> {
  const permissionNames = await readPermissionNames(accessToken);
  const canDeletePermissions = permissionNames.has("permission/delete");
  const canManagePermissions = permissionNames.has("permission/manage");
  const canViewPermissions = permissionNames.has("permission/view");

  if (!canViewPermissions) {
    return {
      canDeletePermissions,
      canManagePermissions,
      canViewPermissions,
      permissions: emptyPermissions(state.limit),
    };
  }

  const permissions = await getPermissions(
    {
      cursor_id: optionalQueryValue(state.cursorId),
      limit: state.limit,
      page: 0,
      search: optionalQueryValue(state.search),
    },
    { accessToken },
  );

  return {
    canDeletePermissions,
    canManagePermissions,
    canViewPermissions,
    permissions,
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

function emptyPermissions(limit: number): PermissionsResponse {
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
