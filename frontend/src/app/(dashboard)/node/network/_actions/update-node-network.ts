"use server";

import { revalidatePath } from "next/cache";

import { isApiError } from "@/lib/api/client";
import {
  createNodeNetwork,
  deleteNodeNetwork,
  updateNodeNetwork,
} from "@/lib/api/node-network";
import { getAuthSession } from "@/lib/auth/session";

const NODE_NETWORKS_PATH = "/node/network";
const MAX_PAN_ID = 0xffff;

export type NodeNetworkActionResult =
  | {
      ok: true;
    }
  | {
      error: string;
      ok: false;
    };

export async function createNodeNetworkAction({
  description,
  name,
  panId,
}: {
  description: string;
  name: string;
  panId: string;
}): Promise<NodeNetworkActionResult> {
  if (!name) {
    return missingNameResult();
  }

  const parsedPanId = parsePanId(panId);
  if (parsedPanId === null) {
    return invalidPanIdResult();
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("creating node networks");
  }

  try {
    await createNodeNetwork(
      {
        description,
        name,
        pan_id: parsedPanId,
      },
      { accessToken: session.accessToken },
    );
    revalidatePath(NODE_NETWORKS_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The node network could not be created.");
  }
}

export async function updateNodeNetworkAction({
  description,
  name,
  nodeNetworkId,
  panId,
}: {
  description: string;
  name: string;
  nodeNetworkId: string;
  panId: string;
}): Promise<NodeNetworkActionResult> {
  if (!nodeNetworkId) {
    return {
      error: "Select a node network before updating.",
      ok: false,
    };
  }

  if (!name) {
    return missingNameResult();
  }

  const parsedPanId = parsePanId(panId);
  if (parsedPanId === null) {
    return invalidPanIdResult();
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("updating node networks");
  }

  try {
    await updateNodeNetwork(
      nodeNetworkId,
      {
        description,
        name,
        pan_id: parsedPanId,
      },
      { accessToken: session.accessToken },
    );
    revalidatePath(NODE_NETWORKS_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The node network could not be updated.");
  }
}

export async function deleteNodeNetworkAction(
  nodeNetworkId: string,
): Promise<NodeNetworkActionResult> {
  if (!nodeNetworkId) {
    return {
      error: "Select a node network before deleting.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return expiredSessionResult("deleting node networks");
  }

  try {
    await deleteNodeNetwork(nodeNetworkId, { accessToken: session.accessToken });
    revalidatePath(NODE_NETWORKS_PATH);
    return { ok: true };
  } catch (error) {
    return actionErrorResult(error, "The node network could not be deleted.");
  }
}

function missingNameResult(): NodeNetworkActionResult {
  return {
    error: "Node network name is required.",
    ok: false,
  };
}

function invalidPanIdResult(): NodeNetworkActionResult {
  return {
    error: `PAN ID must be a whole number from 0 to ${MAX_PAN_ID}.`,
    ok: false,
  };
}

function parsePanId(value: string): number | null {
  const panId = Number(value);
  if (!value || !Number.isInteger(panId) || panId < 0 || panId > MAX_PAN_ID) {
    return null;
  }

  return panId;
}

function expiredSessionResult(action: string): NodeNetworkActionResult {
  return {
    error: `Your session has expired. Sign in again before ${action}.`,
    ok: false,
  };
}

function actionErrorResult(
  error: unknown,
  fallback: string,
): NodeNetworkActionResult {
  return {
    error: isApiError(error) ? error.message : fallback,
    ok: false,
  };
}
