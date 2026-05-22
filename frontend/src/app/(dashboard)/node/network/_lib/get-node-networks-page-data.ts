import {
  getNodeNetworks,
  type NodeNetworksResponse,
} from "@/lib/api/node-network";
import { getMyPermissions } from "@/lib/api/user";

import type { CursorListState } from "../../../admin/_lib/cursor-list-state";

export type NodeNetworksPageData = {
  canDeleteNodeNetworks: boolean;
  canManageNodeNetworks: boolean;
  canViewNodeNetworks: boolean;
  nodeNetworks: NodeNetworksResponse;
};

export async function getNodeNetworksPageData(
  accessToken: string,
  state: CursorListState,
): Promise<NodeNetworksPageData> {
  const permissionNames = await readPermissionNames(accessToken);
  const canDeleteNodeNetworks = permissionNames.has("node-network/delete");
  const canManageNodeNetworks = permissionNames.has("node-network/manage");
  const canViewNodeNetworks = permissionNames.has("node-network/view");

  if (!canViewNodeNetworks) {
    return {
      canDeleteNodeNetworks,
      canManageNodeNetworks,
      canViewNodeNetworks,
      nodeNetworks: emptyNodeNetworks(state.limit),
    };
  }

  const nodeNetworks = await getNodeNetworks(
    {
      cursor_id: optionalQueryValue(state.cursorId),
      limit: state.limit,
      page: 0,
      search: optionalQueryValue(state.search),
    },
    { accessToken },
  );

  return {
    canDeleteNodeNetworks,
    canManageNodeNetworks,
    canViewNodeNetworks,
    nodeNetworks,
  };
}

async function readPermissionNames(accessToken: string): Promise<Set<string>> {
  try {
    const permissions = await getMyPermissions({ accessToken });
    return new Set(permissions.map((permission) => permission.name));
  } catch {
    return new Set();
  }
}

function emptyNodeNetworks(limit: number): NodeNetworksResponse {
  return {
    data: [],
    meta: {
      limit,
      page: 0,
      total: 0,
    },
  };
}

function optionalQueryValue(value: string): string | undefined {
  return value || undefined;
}
