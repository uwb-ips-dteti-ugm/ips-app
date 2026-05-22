import { getNodes } from "@/lib/api/node";
import { getMyPermissions } from "@/lib/api/user";

export type RangeMonitorNodeOption = {
  address: number;
  deviceId: string;
  id: string;
  name: string;
  network: {
    id: string;
    name: string;
    panId: number;
  };
};

export type RangeMonitorPageData = {
  canViewRangeMonitor: boolean;
  nodes: RangeMonitorNodeOption[];
};

export async function getRangeMonitorPageData(
  accessToken: string,
): Promise<RangeMonitorPageData> {
  const permissionNames = await readPermissionNames(accessToken);
  const canViewRangeMonitor =
    permissionNames.has("node/view") && permissionNames.has("record/view");

  if (!canViewRangeMonitor) {
    return {
      canViewRangeMonitor,
      nodes: [],
    };
  }

  const nodes = await getNodes(
    {
      limit: 500,
      page: 0,
      status: "approved",
    },
    { accessToken },
  );

  return {
    canViewRangeMonitor,
    nodes: nodes.data.flatMap((node) => {
      if (!node.network || node.address === null) {
        return [];
      }

      return [
        {
          address: node.address,
          deviceId: node.device_id,
          id: node.id,
          name: node.name,
          network: {
            id: node.network.id,
            name: node.network.name,
            panId: node.network.pan_id,
          },
        },
      ];
    }),
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
