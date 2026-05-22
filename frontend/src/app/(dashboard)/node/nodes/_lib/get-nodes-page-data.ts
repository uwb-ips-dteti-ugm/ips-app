import { getNodes, type NodesResponse } from "@/lib/api/node";
import { getNodeNetworks } from "@/lib/api/node-network";
import { getMyPermissions } from "@/lib/api/user";

import type { NodesListState } from "./nodes-list-state";

export type NodeNetworkFilterOption = {
  id: string;
  name: string;
  panId: number;
};

export type NodesPageData = {
  canManageNodes: boolean;
  canViewNodes: boolean;
  networks: NodeNetworkFilterOption[];
  nodes: NodesResponse;
};

export async function getNodesPageData(
  accessToken: string,
  state: NodesListState,
): Promise<NodesPageData> {
  const permissionNames = await readPermissionNames(accessToken);
  const canManageNodes = permissionNames.has("node/manage");
  const canViewNodes = permissionNames.has("node/view");

  if (!canViewNodes) {
    return {
      canManageNodes,
      canViewNodes,
      networks: [],
      nodes: emptyNodes(state.limit),
    };
  }

  const [nodes, networks] = await Promise.all([
    getNodes(
      {
        address: optionalAddressValue(state.address),
        cursor_id: optionalQueryValue(state.cursorId),
        limit: state.limit,
        network_id: optionalQueryValue(state.networkId),
        page: 0,
        search: optionalQueryValue(state.search),
        status: state.status || undefined,
      },
      { accessToken },
    ),
    permissionNames.has("node-network/view")
      ? readNetworkOptions(accessToken)
      : [],
  ]);

  return {
    canManageNodes,
    canViewNodes,
    networks,
    nodes,
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

async function readNetworkOptions(
  accessToken: string,
): Promise<NodeNetworkFilterOption[]> {
  try {
    const networks = await getNodeNetworks(
      { limit: 500, page: 0 },
      { accessToken },
    );

    return networks.data.map((network) => ({
      id: network.id,
      name: network.name,
      panId: network.pan_id,
    }));
  } catch {
    return [];
  }
}

function emptyNodes(limit: number): NodesResponse {
  return {
    data: [],
    meta: {
      limit,
      page: 0,
      total: 0,
    },
  };
}

function optionalAddressValue(value: string): number | undefined {
  return value ? Number(value) : undefined;
}

function optionalQueryValue(value: string): string | undefined {
  return value || undefined;
}
