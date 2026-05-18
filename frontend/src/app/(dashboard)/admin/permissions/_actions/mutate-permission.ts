"use server";

import { revalidatePath } from "next/cache";

import {
  getActionAccessToken,
  fetchBackend,
  jsonBackend,
} from "@/lib/actions/backend";
import {
  type ActionState,
  getFormString,
  readErrorMessage,
} from "@/lib/actions/form";

export async function createPermissionAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const accessToken = await getActionAccessToken();
  const name = getFormString(formData, "name");
  const description = getFormString(formData, "description");

  if (!name) {
    return { status: "error", message: "Name is required." };
  }

  const response = await jsonBackend(accessToken, "/permissions", "POST", {
    name,
    description,
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to register permission."),
    };
  }

  revalidatePath("/admin/permissions");
  return { status: "success", message: "Permission registered successfully." };
}

export async function updatePermissionAction(
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

  const response = await jsonBackend(accessToken, `/permissions/${id}`, "PATCH", {
    name,
    description,
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to update permission."),
    };
  }

  revalidatePath("/admin/permissions");
  return { status: "success", message: "Permission updated successfully." };
}

export async function deletePermissionAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const accessToken = await getActionAccessToken();
  const id = getFormString(formData, "id");

  if (!id) {
    return { status: "error", message: "Permission ID is required." };
  }

  const response = await fetchBackend(accessToken, `/permissions/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to delete permission."),
    };
  }

  revalidatePath("/admin/permissions");
  return { status: "success", message: "Permission deleted successfully." };
}
