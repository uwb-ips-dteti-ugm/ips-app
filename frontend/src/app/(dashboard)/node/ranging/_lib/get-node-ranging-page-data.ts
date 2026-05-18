import { canAccessFeature } from "@/lib/api/featureAccess";
import {
  fetchNodeByDeviceId,
  fetchNodes,
  type NodeListItem,
} from "@/lib/api/nodes";
import {
  fetchRangingRecordsByPair,
  getLatestRangingRecord,
  type RangingRecord,
} from "@/lib/api/records";
import { getStringParam } from "@/lib/navigation/searchParams";

export type NodeRangingPageSearchParams = Record<
  string,
  string | string[] | undefined
>;

export type NodeRangingPageData = {
  canViewNodes: boolean;
  canViewRecords: boolean;
  sourceSearch: string;
  targetSearch: string;
  sourceNodeDeviceId: string;
  targetNodeDeviceId: string;
  sourceNodes: NodeListItem[];
  targetNodes: NodeListItem[];
  latestRecord: RangingRecord | null;
};

export async function getNodeRangingPageData(
  accessToken: string,
  searchParams: NodeRangingPageSearchParams,
): Promise<NodeRangingPageData> {
  const [canViewNodes, canViewRecords] = await Promise.all([
    canAccessFeature(accessToken, "node/view"),
    canAccessFeature(accessToken, "record/view"),
  ]);
  const sourceSearch = getStringParam(searchParams.source_search);
  const targetSearch = getStringParam(searchParams.target_search);
  const sourceNodeDeviceId = getStringParam(searchParams.source_node_device_id);
  const targetNodeDeviceId = getStringParam(searchParams.target_node_device_id);

  if (!canViewNodes || !canViewRecords) {
    return {
      canViewNodes,
      canViewRecords,
      sourceSearch,
      targetSearch,
      sourceNodeDeviceId,
      targetNodeDeviceId,
      sourceNodes: [],
      targetNodes: [],
      latestRecord: null,
    };
  }

  const [sourceNodes, targetNodes, latestRecord] = await Promise.all([
    getApprovedNodeOptions(accessToken, sourceSearch, sourceNodeDeviceId),
    getApprovedNodeOptions(accessToken, targetSearch, targetNodeDeviceId),
    getLatestSelectedPairRecord(
      accessToken,
      sourceNodeDeviceId,
      targetNodeDeviceId,
    ),
  ]);

  return {
    canViewNodes,
    canViewRecords,
    sourceSearch,
    targetSearch,
    sourceNodeDeviceId,
    targetNodeDeviceId,
    sourceNodes,
    targetNodes,
    latestRecord,
  };
}

async function getApprovedNodeOptions(
  accessToken: string,
  search: string,
  selectedDeviceId: string,
): Promise<NodeListItem[]> {
  const nodes = await fetchNodes({
    accessToken,
    status: "approved",
    search,
    limit: 100,
  });
  const options = [...nodes.data];

  if (
    selectedDeviceId &&
    !options.some((node) => node.device_id === selectedDeviceId)
  ) {
    const selectedNode = await fetchNodeByDeviceId(accessToken, selectedDeviceId);
    if (selectedNode?.status === "approved") {
      options.unshift(selectedNode);
    }
  }

  return options;
}

async function getLatestSelectedPairRecord(
  accessToken: string,
  sourceNodeDeviceId: string,
  targetNodeDeviceId: string,
): Promise<RangingRecord | null> {
  if (
    !sourceNodeDeviceId ||
    !targetNodeDeviceId ||
    sourceNodeDeviceId === targetNodeDeviceId
  ) {
    return null;
  }

  const records = await fetchRangingRecordsByPair({
    accessToken,
    sourceNodeDeviceId,
    targetNodeDeviceId,
    start: new Date(0),
    end: new Date(),
  });
  return getLatestRangingRecord(records);
}
