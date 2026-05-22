"use server";

import { revalidatePath } from "next/cache";

import { isApiError } from "@/lib/api/client";
import {
  createPermission,
  deletePermission,
  updatePermission,
} from "@/lib/api/permission";
import { getAuthSession } from "@/lib/auth/session";

const PERMISSIONS_PATH = "/admin/permissions";

export type PermissionActionResult =
  | {
      ok: true;
    }
  | {
      error: string;
      ok: false;
    };

export async function createPermissionAction({
  description,
  name,
}: {
  description: string;
  name: string;
}): Promise<PermissionActionResult> {
  if (!name) {
    return {
      error: "Permission name is required.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("creating permissions");
  }

  try {
    await createPermission(
      { description, name },
      { accessToken: session.accessToken },
    );
    revalidatePath(PERMISSIONS_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The permission could not be created.");
  }
}

export async function updatePermissionAction({
  description,
  name,
  permissionId,
}: {
  description: string;
  name: string;
  permissionId: string;
}): Promise<PermissionActionResult> {
  if (!permissionId || !name) {
    return {
      error: "Permission name is required.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("updating permissions");
  }

  try {
    await updatePermission(
      permissionId,
      { description, name },
      { accessToken: session.accessToken },
    );
    revalidatePath(PERMISSIONS_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The permission could not be updated.");
  }
}

export async function deletePermissionAction(
  permissionId: string,
): Promise<PermissionActionResult> {
  if (!permissionId) {
    return {
      error: "Select a permission before deleting.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("deleting permissions");
  }

  try {
    await deletePermission(permissionId, { accessToken: session.accessToken });
    revalidatePath(PERMISSIONS_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The permission could not be deleted.");
  }
}

function expiredSessionResult(action: string): PermissionActionResult {
  return {
    error: `Your session has expired. Sign in again before ${action}.`,
    ok: false,
  };
}

function actionErrorResult(
  error: unknown,
  fallback: string,
): PermissionActionResult {
  return {
    error: isApiError(error) ? error.message : fallback,
    ok: false,
  };
}
