"use server";

import { revalidatePath } from "next/cache";

import {
  fetchBackend,
  getActionAccessToken,
  jsonBackend,
} from "@/lib/actions/backend";
import { getFormString, readErrorMessage } from "@/lib/actions/form";
import { type NodeStatus } from "@/lib/api/nodes";

const NODE_LIST_PATH = "/node/list";
const NODE_STATUSES = new Set<NodeStatus>([
  "pending",
  "approved",
  "suspended",
  "revoked",
]);

export async function setNodeStatusAction(formData: FormData): Promise<void> {
  const accessToken = await getActionAccessToken();
  const nodeId = getFormString(formData, "node_id");
  const status = getFormString(formData, "status") as NodeStatus;

  if (!nodeId || !NODE_STATUSES.has(status)) {
    throw new Error("Node ID and valid status are required.");
  }

  const response = await jsonBackend(accessToken, `/nodes/${nodeId}/status`, "PATCH", {
    status,
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to update node status."));
  }

  revalidatePath(NODE_LIST_PATH);
}

export async function restartNodeAction(formData: FormData): Promise<void> {
  const accessToken = await getActionAccessToken();
  const deviceId = getFormString(formData, "device_id");

  if (!deviceId) {
    throw new Error("Device ID is required.");
  }

  const response = await fetchBackend(
    accessToken,
    `/nodes/device/${deviceId}/restart`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to restart node."));
  }

  revalidatePath(NODE_LIST_PATH);
}

export async function deleteNodeAction(formData: FormData): Promise<void> {
  const accessToken = await getActionAccessToken();
  const nodeId = getFormString(formData, "node_id");

  if (!nodeId) {
    throw new Error("Node ID is required.");
  }

  const response = await fetchBackend(accessToken, `/nodes/${nodeId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to delete node."));
  }

  revalidatePath(NODE_LIST_PATH);
}
