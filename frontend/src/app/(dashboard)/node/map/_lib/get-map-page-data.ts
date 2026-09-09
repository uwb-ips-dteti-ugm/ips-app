import { getNodes } from "@/lib/api/node";
import { getMyPermissions } from "@/lib/api/user";

import { LAB_DASAR_ANCHORS, type LabDasarAnchorConfig } from "./lab-dasar-room";

export type MapAnchorNode = LabDasarAnchorConfig & {
  id: string;
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

  const anchorConfigByDeviceId = new Map(
    LAB_DASAR_ANCHORS.map((anchor) => [anchor.deviceId, anchor]),
  );

  const anchors: MapAnchorNode[] = [];
  let anchorNetworkId: string | null = null;

  for (const node of nodes.items) {
    const anchorConfig = anchorConfigByDeviceId.get(node.device_id);
    if (!anchorConfig) {
      continue;
    }

    // The node's persisted position (editable via the node admin UI, and what
    // the backend trilateration solve actually uses) is the source of truth
    // once set. The survey constant is only a fallback for anchors that
    // haven't had their position edited yet.
    const position = node.position ?? anchorConfig;

    anchors.push({ ...anchorConfig, ...position, id: node.id });
    anchorNetworkId = node.network?.id ?? anchorNetworkId;
  }

  const tagCandidates: MapTagCandidate[] = anchorNetworkId
    ? nodes.items.flatMap((node) => {
        const isAnchor = anchorConfigByDeviceId.has(node.device_id);
        if (isAnchor || node.network?.id !== anchorNetworkId || node.address === null) {
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
