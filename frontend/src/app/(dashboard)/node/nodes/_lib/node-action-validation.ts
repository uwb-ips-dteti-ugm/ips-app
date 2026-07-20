import type { NodeStatus } from "@/lib/api/node";

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
