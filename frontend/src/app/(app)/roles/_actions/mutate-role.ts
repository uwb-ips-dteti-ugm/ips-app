"use server";

import { revalidatePath } from "next/cache";

import {
  fetchBackend,
  getActionAccessToken,
  jsonBackend,
} from "@/lib/actions/backend";
import {
  type ActionState,
  getFormString,
  readErrorMessage,
} from "@/lib/actions/form";
import {
  getFormStringList,
  replaceAssignedPermissions,
} from "@/lib/actions/permissions";

export async function createRoleAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const accessToken = await getActionAccessToken();
  const name = getFormString(formData, "name");
  const description = getFormString(formData, "description");

  if (!name) {
    return { status: "error", message: "Name is required." };
  }

  const response = await jsonBackend(accessToken, "/roles", "POST", {
    name,
    description,
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to register role."),
    };
  }

  revalidatePath("/roles");
  return { status: "success", message: "Role registered successfully." };
}

export async function updateRoleAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const accessToken = await getActionAccessToken();
  const id = getFormString(formData, "id");
  const name = getFormString(formData, "name");
  const description = getFormString(formData, "description");

  if (!id || !name) {
    return { status: "error", message: "Name is required." };
  }

  const response = await jsonBackend(accessToken, `/roles/${id}`, "PATCH", {
    name,
    description,
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to update role."),
    };
  }

  revalidatePath("/roles");
  return { status: "success", message: "Role updated successfully." };
}

export async function deleteRoleAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const accessToken = await getActionAccessToken();
  const id = getFormString(formData, "id");

  if (!id) {
    return { status: "error", message: "Role ID is required." };
  }

  const response = await fetchBackend(accessToken, `/roles/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to delete role."),
    };
  }

  revalidatePath("/roles");
  return { status: "success", message: "Role deleted successfully." };
}

export async function assignRolePermissionsAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const accessToken = await getActionAccessToken();
  const id = getFormString(formData, "id");
  const selectedPermissionIds = getFormStringList(formData, "permission_ids");
  const assignedPermissionIds = getFormStringList(
    formData,
    "assigned_permission_ids",
  );

  if (!id) {
    return { status: "error", message: "Role ID is required." };
  }

  const result = await replaceAssignedPermissions({
    accessToken,
    path: `/roles/${id}/permissions`,
    selectedPermissionIds,
    assignedPermissionIds,
  });

  if (result.status === "error") {
    return result;
  }

  revalidatePath("/roles");
  return { status: "success", message: "Role permissions updated successfully." };
}
