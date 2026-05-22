"use server";

import { revalidatePath } from "next/cache";

import { isApiError } from "@/lib/api/client";
import {
  addRolePermissions,
  createRole,
  deleteRole,
  removeRolePermissions,
  setDefaultRole,
  updateRole,
} from "@/lib/api/role";
import { getAuthSession } from "@/lib/auth/session";

const ROLES_PATH = "/admin/roles";

export type RoleActionResult =
  | {
      ok: true;
    }
  | {
      error: string;
      ok: false;
    };

export async function createRoleAction({
  description,
  isDefault,
  name,
}: {
  description: string;
  isDefault: boolean;
  name: string;
}): Promise<RoleActionResult> {
  if (!name) {
    return {
      error: "Role name is required.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("creating roles");
  }

  try {
    await createRole(
      {
        description,
        is_default: isDefault,
        name,
      },
      { accessToken: session.accessToken },
    );
    revalidatePath(ROLES_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The role could not be created.");
  }
}

export async function updateRoleAction({
  description,
  makeDefault,
  name,
  roleId,
}: {
  description: string;
  makeDefault: boolean;
  name: string;
  roleId: string;
}): Promise<RoleActionResult> {
  if (!roleId || !name) {
    return {
      error: "Role name is required.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("updating roles");
  }

  try {
    await updateRole(
      roleId,
      { description, name },
      { accessToken: session.accessToken },
    );
    if (makeDefault) {
      await setDefaultRole(roleId, { accessToken: session.accessToken });
    }
    revalidatePath(ROLES_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The role could not be updated.");
  }
}

export async function deleteRoleAction(roleId: string): Promise<RoleActionResult> {
  if (!roleId) {
    return {
      error: "Select a role before deleting.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("deleting roles");
  }

  try {
    await deleteRole(roleId, { accessToken: session.accessToken });
    revalidatePath(ROLES_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The role could not be deleted.");
  }
}

export async function setDefaultRoleAction(
  roleId: string,
): Promise<RoleActionResult> {
  if (!roleId) {
    return {
      error: "Select a role before setting it as default.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("setting default roles");
  }

  try {
    await setDefaultRole(roleId, { accessToken: session.accessToken });
    revalidatePath(ROLES_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The default role could not be updated.");
  }
}

export async function updateRolePermissionsAction({
  currentPermissionIds,
  nextPermissionIds,
  roleId,
}: {
  currentPermissionIds: string[];
  nextPermissionIds: string[];
  roleId: string;
}): Promise<RoleActionResult> {
  if (!roleId) {
    return {
      error: "Select a role before updating permissions.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("updating role permissions");
  }

  const currentIds = new Set(currentPermissionIds);
  const nextIds = new Set(nextPermissionIds);
  const permissionIdsToAdd = nextPermissionIds.filter((id) => !currentIds.has(id));
  const permissionIdsToRemove = currentPermissionIds.filter((id) => !nextIds.has(id));

  try {
    if (permissionIdsToAdd.length > 0) {
      await addRolePermissions(
        roleId,
        { permission_ids: permissionIdsToAdd },
        { accessToken: session.accessToken },
      );
    }

    if (permissionIdsToRemove.length > 0) {
      await removeRolePermissions(
        roleId,
        { permission_ids: permissionIdsToRemove },
        { accessToken: session.accessToken },
      );
    }

    revalidatePath(ROLES_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The role permissions could not be updated.");
  }
}

function expiredSessionResult(action: string): RoleActionResult {
  return {
    error: `Your session has expired. Sign in again before ${action}.`,
    ok: false,
  };
}

function actionErrorResult(error: unknown, fallback: string): RoleActionResult {
  return {
    error: isApiError(error) ? error.message : fallback,
    ok: false,
  };
}
