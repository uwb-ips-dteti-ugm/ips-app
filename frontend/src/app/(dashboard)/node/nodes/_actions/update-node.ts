"use server";

import { revalidatePath } from "next/cache";

import { isApiError } from "@/lib/api/client";
import {
  updateNodeInfo,
  updateNodeNetworkAssignment,
  updateNodeStatus,
} from "@/lib/api/node";
import { getAuthSession } from "@/lib/auth/session";

import {
  NODES_PATH,
  parseNetworkAssignment,
  parseNodeStatus,
  validateNodeName,
  type NodeActionResult,
} from "../_lib/node-action-validation";

export async function updateNodeAction({
  address,
  description,
  name,
  networkId,
  nodeId,
  status,
}: {
  address: string;
  description: string;
  name: string;
  networkId: string;
  nodeId: string;
  status: string;
}): Promise<NodeActionResult> {
  if (!nodeId) {
    return {
      error: "Select a node before updating it.",
      ok: false,
    };
  }

  const nameError = validateNodeName(name);
  if (nameError) {
    return {
      error: nameError,
      ok: false,
    };
  }

  const parsedStatus = parseNodeStatus(status);
  if (parsedStatus === null) {
    return {
      error: "Select a valid node status.",
      ok: false,
    };
  }

  const parsedAssignment = parseNetworkAssignment(networkId, address);
  if (!parsedAssignment.ok) {
    return parsedAssignment;
  }

  if (parsedStatus === "approved" && parsedAssignment.networkId === null) {
    return {
      error: "Approved nodes must have a network and address.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before updating nodes.",
      ok: false,
    };
  }

  try {
    await updateNodeNetworkAssignment(
      nodeId,
      {
        address: parsedAssignment.address,
        network_id: parsedAssignment.networkId,
      },
      { accessToken: session.accessToken },
    );
    await updateNodeInfo(
      nodeId,
      {
        description,
        name: name.trim(),
      },
      { accessToken: session.accessToken },
    );
    await updateNodeStatus(
      nodeId,
      { status: parsedStatus },
      { accessToken: session.accessToken },
    );
    revalidatePath(NODES_PATH);
    return { ok: true };
  } catch (error) {
    return {
      error: isApiError(error) ? error.message : "The node could not be updated.",
      ok: false,
    };
  }
}
