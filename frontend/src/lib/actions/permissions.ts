import { jsonBackend } from "@/lib/actions/backend";
import { type ActionState, readErrorMessage } from "@/lib/actions/form";

export async function replaceAssignedPermissions({
  accessToken,
  path,
  selectedPermissionIds,
  assignedPermissionIds,
}: {
  accessToken: string;
  path: string;
  selectedPermissionIds: string[];
  assignedPermissionIds: string[];
}): Promise<ActionState> {
  const selected = new Set(selectedPermissionIds);
  const assigned = new Set(assignedPermissionIds);
  const toAdd = selectedPermissionIds.filter((id) => !assigned.has(id));
  const toRemove = assignedPermissionIds.filter((id) => !selected.has(id));

  if (toAdd.length > 0) {
    const response = await jsonBackend(accessToken, path, "POST", {
      permission_ids: toAdd,
    });
    if (!response.ok) {
      return {
        status: "error",
        message: await readErrorMessage(response, "Failed to add permissions."),
      };
    }
  }

  if (toRemove.length > 0) {
    const response = await jsonBackend(accessToken, path, "DELETE", {
      permission_ids: toRemove,
    });
    if (!response.ok) {
      return {
        status: "error",
        message: await readErrorMessage(response, "Failed to remove permissions."),
      };
    }
  }

  return { status: "success", message: "Permissions updated successfully." };
}

export function getFormStringList(formData: FormData, key: string): string[] {
  return formData
    .getAll(key)
    .filter((value): value is string => typeof value === "string")
    .map((value) => value.trim())
    .filter(Boolean);
}
