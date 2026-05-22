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
  validateNodeName,
} from "../_lib/node-action-validation";

export type NodeApprovalActionResult =
  | {
      ok: true;
    }
  | {
      error: string;
      ok: false;
    };

export async function approveNodeAction({
  address,
  name,
  networkId,
  nodeId,
}: {
  address: string;
  name: string;
  networkId: string;
  nodeId: string;
}): Promise<NodeApprovalActionResult> {
  if (!nodeId) {
    return {
      error: "Select a pending node before approving it.",
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

  const parsedAssignment = parseNetworkAssignment(networkId, address);
  if (!parsedAssignment.ok) {
    return parsedAssignment;
  }

  if (parsedAssignment.networkId === null || parsedAssignment.address === null) {
    return {
      error: "Select a node network and address before approving this node.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before approving nodes.",
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
        name: name.trim(),
      },
      { accessToken: session.accessToken },
    );
    await updateNodeStatus(
      nodeId,
      { status: "approved" },
      { accessToken: session.accessToken },
    );
    revalidatePath(NODES_PATH);
    return { ok: true };
  } catch (error) {
    return {
      error: isApiError(error)
        ? error.message
        : "The node could not be approved.",
      ok: false,
    };
  }
}
