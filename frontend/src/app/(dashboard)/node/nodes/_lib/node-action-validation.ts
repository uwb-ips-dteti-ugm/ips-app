import type { NodeRole, NodeStatus, PositionValue } from "@/lib/api/node";

export const NODES_PATH = "/node/nodes";
export const MAX_UWB_ADDRESS = 0xffff;

export type NodeActionResult =
  | {
      ok: true;
    }
  | {
      error: string;
      ok: false;
    };

type NetworkAssignmentParseResult =
  | {
      address: number | null;
      networkId: string | null;
      ok: true;
    }
  | {
      error: string;
      ok: false;
    };

export function validateNodeName(value: string): string | null {
  const name = value.trim();
  if (name.length < 2 || name.length > 100) {
    return "Name must be between 2 and 100 characters.";
  }

  if (!/^[\p{L}\p{N}_\s'-]+$/u.test(name)) {
    return "Name contains invalid characters.";
  }

  return null;
}

export function parseNetworkAssignment(
  networkId: string,
  address: string,
): NetworkAssignmentParseResult {
  const trimmedNetworkId = networkId.trim();
  const trimmedAddress = address.trim();

  if (!trimmedNetworkId && !trimmedAddress) {
    return {
      address: null,
      networkId: null,
      ok: true,
    };
  }

  if (!trimmedNetworkId || !trimmedAddress) {
    return {
      error: "Network and address must be provided together.",
      ok: false,
    };
  }

  const parsedAddress = parseAddress(trimmedAddress);
  if (parsedAddress === null) {
    return {
      error: `Address must be a whole number from 0 to ${MAX_UWB_ADDRESS}.`,
      ok: false,
    };
  }

  return {
    address: parsedAddress,
    networkId: trimmedNetworkId,
    ok: true,
  };
}

type PositionParseResult =
  | {
      ok: true;
      shouldUpdate: false;
    }
  | {
      ok: true;
      position: PositionValue;
      shouldUpdate: true;
    }
  | {
      error: string;
      ok: false;
    };

// Position is optional and rarely edited, so leaving all three fields blank
// means "leave the existing position alone" (not "clear it") -- clearing
// requires a dedicated action, not an accidental blank submit.
export function parsePositionInput(
  x: string,
  y: string,
  z: string,
): PositionParseResult {
  const trimmedX = x.trim();
  const trimmedY = y.trim();
  const trimmedZ = z.trim();

  if (!trimmedX && !trimmedY && !trimmedZ) {
    return { ok: true, shouldUpdate: false };
  }

  if (!trimmedX || !trimmedY || !trimmedZ) {
    return {
      error: "Provide x, y, and z together to set a fixed position.",
      ok: false,
    };
  }

  const parsedX = Number(trimmedX);
  const parsedY = Number(trimmedY);
  const parsedZ = Number(trimmedZ);

  if (![parsedX, parsedY, parsedZ].every(Number.isFinite)) {
    return {
      error: "Position x, y, and z must be numbers.",
      ok: false,
    };
  }

  return {
    ok: true,
    position: { x: parsedX, y: parsedY, z: parsedZ },
    shouldUpdate: true,
  };
}

type RoleParseResult =
  | {
      ok: true;
      role: NodeRole | null;
    }
  | {
      error: string;
      ok: false;
    };

// Empty string means "unset" (null) -- clearing a role is valid, unlike an
// unrecognized value.
export function parseNodeRole(value: string): RoleParseResult {
  const trimmed = value.trim();
  if (!trimmed) {
    return { ok: true, role: null };
  }
  if (trimmed !== "anchor" && trimmed !== "tag") {
    return { error: "Select a valid node role.", ok: false };
  }
  return { ok: true, role: trimmed };
}

export function parseNodeStatus(value: string): NodeStatus | null {
  return ["pending", "approved", "suspended"].includes(value)
    ? (value as NodeStatus)
    : null;
}

function parseAddress(value: string): number | null {
  const address = Number(value);
  if (
    !value ||
    !Number.isInteger(address) ||
    address < 0 ||
    address > MAX_UWB_ADDRESS
  ) {
    return null;
  }

  return address;
}
