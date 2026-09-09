import { getNodes } from "@/lib/api/node";
import { getMyPermissions } from "@/lib/api/user";

const UNSET_POSITION_FALLBACK = { x: 0, y: 0, z: 0 };

export type MapAnchorNode = {
  deviceId: string;
  id: string;
  label: string;
  x: number;
  y: number;
  z: number;
};

export type MapTagCandidate = {
  address: number;
  deviceId: string;
  id: string;
  name: string;
};

export type MapPageData = {
  anchors: MapAnchorNode[];
  canViewMap: boolean;
  tagCandidates: MapTagCandidate[];
};

export async function getMapPageData(accessToken: string): Promise<MapPageData> {
  const permissionNames = await readPermissionNames(accessToken);
  const canViewMap =
    permissionNames.has("node/view") && permissionNames.has("ranging/view");

  if (!canViewMap) {
    return { anchors: [], canViewMap, tagCandidates: [] };
  }

  const nodes = await getNodes(
    { limit: 100, page: 0, status: "approved" },
    { accessToken },
  );

  const anchors: MapAnchorNode[] = [];
  let anchorNetworkId: string | null = null;

  for (const node of nodes.items) {
    if (node.role !== "anchor") {
      continue;
    }

    // The node's persisted position (editable via the node admin UI, and what
    // the backend trilateration solve actually uses) is the source of truth.
    // An anchor that hasn't had its position set yet falls back to the
    // origin rather than being dropped from the map.
    const position = node.position ?? UNSET_POSITION_FALLBACK;

    anchors.push({
      deviceId: node.device_id,
      label: node.name,
      ...position,
      id: node.id,
    });
    anchorNetworkId = node.network?.id ?? anchorNetworkId;
  }

  const tagCandidates: MapTagCandidate[] = anchorNetworkId
    ? nodes.items.flatMap((node) => {
        if (node.role === "anchor" || node.network?.id !== anchorNetworkId || node.address === null) {
          return [];
        }

        return [
          {
            address: node.address,
            deviceId: node.device_id,
            id: node.id,
            name: node.name,
          },
        ];
      })
    : [];

  return { anchors, canViewMap, tagCandidates };
}

async function readPermissionNames(accessToken: string): Promise<Set<string>> {
  try {
    const permissions = await getMyPermissions({ accessToken });
    return new Set(permissions.map((permission) => permission.name));
  } catch {
    return new Set();
  }
}
