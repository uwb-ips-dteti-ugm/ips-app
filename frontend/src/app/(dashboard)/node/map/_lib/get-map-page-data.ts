import { getNodes } from "@/lib/api/node";
import { getMyPermissions } from "@/lib/api/user";

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
    // An anchor only appears on the map once it's actually usable as one:
    // marked as an anchor and given a surveyed position (the same
    // node.position the backend trilateration solve reads).
    if (node.role !== "anchor" || node.position === null) {
      continue;
    }

    anchors.push({
      deviceId: node.device_id,
      label: node.name,
      ...node.position,
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
