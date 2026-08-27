import {
  getRangingRecords,
  type RangingRecordResponse,
} from "@/lib/api/ranging";

// The backend can only filter ranging records by a single node_id (returning
// records where that node is either side of the pair), not "the latest
// between specifically A and B" -- so callers fetch everything touching the
// source node within a recent window and pick the latest per counterpart
// client-side, rather than one /ranging/latest call per target.
const LATEST_RANGE_WINDOW_MS = 10 * 60 * 1000;

export type LatestRange = {
  distance: number;
  recordedAt: string;
  sourceNodeId: string;
  targetNodeId: string;
};

export async function fetchLatestRangesByTarget({
  accessToken,
  sourceNodeId,
  targetNodeIds,
}: {
  accessToken: string;
  sourceNodeId: string;
  targetNodeIds: string[];
}): Promise<Map<string, LatestRange>> {
  if (targetNodeIds.length === 0) {
    return new Map();
  }

  const end = new Date();
  const start = new Date(end.getTime() - LATEST_RANGE_WINDOW_MS);

  const records = await getRangingRecords(
    {
      end: end.toISOString(),
      node_id: sourceNodeId,
      start: start.toISOString(),
    },
    { accessToken },
  );

  return pickLatestRecordPerCounterpart(
    records,
    sourceNodeId,
    new Set(targetNodeIds),
  );
}

function pickLatestRecordPerCounterpart(
  records: RangingRecordResponse[],
  sourceNodeId: string,
  targetNodeIds: Set<string>,
): Map<string, LatestRange> {
  const latestByTargetId = new Map<string, LatestRange>();

  for (const record of records) {
    const counterpart =
      record.listener_node.id === sourceNodeId
        ? record.initiator_node
        : record.listener_node;

    if (!targetNodeIds.has(counterpart.id)) {
      continue;
    }

    const existing = latestByTargetId.get(counterpart.id);
    if (existing && new Date(existing.recordedAt) >= new Date(record.recorded_at)) {
      continue;
    }

    latestByTargetId.set(counterpart.id, {
      distance: record.distance,
      recordedAt: record.recorded_at,
      sourceNodeId,
      targetNodeId: counterpart.id,
    });
  }

  return latestByTargetId;
}
