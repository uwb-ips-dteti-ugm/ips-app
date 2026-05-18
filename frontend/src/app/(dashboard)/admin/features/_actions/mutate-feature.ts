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

export async function createFeatureAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const accessToken = await getActionAccessToken();
  const name = getFormString(formData, "name");
  const description = getFormString(formData, "description");

  if (!name) {
    return { status: "error", message: "Name is required." };
  }

  const response = await jsonBackend(accessToken, "/features", "POST", {
    name,
    description,
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to register feature."),
    };
  }

  revalidatePath("/admin/features");
  return { status: "success", message: "Feature registered successfully." };
}

export async function updateFeatureAction(
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

  const response = await jsonBackend(accessToken, `/features/${id}`, "PATCH", {
    name,
    description,
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to update feature."),
    };
  }

  revalidatePath("/admin/features");
  return { status: "success", message: "Feature updated successfully." };
}

export async function deleteFeatureAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const accessToken = await getActionAccessToken();
  const id = getFormString(formData, "id");

  if (!id) {
    return { status: "error", message: "Feature ID is required." };
  }

  const response = await fetchBackend(accessToken, `/features/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to delete feature."),
    };
  }

  revalidatePath("/admin/features");
  return { status: "success", message: "Feature deleted successfully." };
}

export async function assignFeaturePermissionsAction(
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
    return { status: "error", message: "Feature ID is required." };
  }

  const result = await replaceAssignedPermissions({
    accessToken,
    path: `/features/${id}/permissions`,
    selectedPermissionIds,
    assignedPermissionIds,
  });

  if (result.status === "error") {
    return result;
  }

  revalidatePath("/admin/features");
  return {
    status: "success",
    message: "Feature permissions updated successfully.",
  };
}
