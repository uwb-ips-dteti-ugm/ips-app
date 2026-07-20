"use server";

import {
  getRangingRecords,
  type RangingRecordResponse,
} from "@/lib/api/ranging";
import { getAuthSession } from "@/lib/auth/session";

// The backend can only filter ranging records by a single node_id (returning
// records where that node is either side of the pair), not "the latest
// between specifically A and B" -- so we fetch everything touching the
// source node within a recent window and pick the latest per counterpart
// client-side, rather than one /ranging/latest call per target.
const RANGE_MONITOR_WINDOW_MS = 10 * 60 * 1000;

export type RangeMonitorRange = {
  distance: number;
  recordedAt: string;
  sourceNodeId: string;
  targetNodeId: string;
};

export type RangeMonitorRangeRow = {
  range: RangeMonitorRange | null;
  targetNodeId: string;
};

export type RangeMonitorRangesActionResult =
  | {
      ok: true;
      ranges: RangeMonitorRangeRow[];
    }
  | {
      error: string;
      ok: false;
    };

export async function getRangeMonitorRangesAction({
  sourceNodeId,
  targetNodeIds,
}: {
  sourceNodeId: string;
  targetNodeIds: string[];
}): Promise<RangeMonitorRangesActionResult> {
  if (!sourceNodeId) {
    return {
      error: "Select a node before monitoring ranges.",
      ok: false,
    };
  }

  if (targetNodeIds.length === 0) {
    return {
      ok: true,
      ranges: [],
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again to monitor ranges.",
      ok: false,
    };
  }

  try {
    const end = new Date();
    const start = new Date(end.getTime() - RANGE_MONITOR_WINDOW_MS);

    const records = await getRangingRecords(
      {
        end: end.toISOString(),
        node_id: sourceNodeId,
        start: start.toISOString(),
      },
      { accessToken: session.accessToken },
    );

    const latestByTargetId = pickLatestRecordPerCounterpart(
      records,
      sourceNodeId,
      new Set(targetNodeIds),
    );

    return {
      ok: true,
      ranges: targetNodeIds.map((targetNodeId) => ({
        range: toRange(latestByTargetId.get(targetNodeId), sourceNodeId, targetNodeId),
        targetNodeId,
      })),
    };
  } catch {
    return {
      error: "The latest ranges could not be loaded. Please try again.",
      ok: false,
    };
  }
}

function pickLatestRecordPerCounterpart(
  records: RangingRecordResponse[],
  sourceNodeId: string,
  targetNodeIds: Set<string>,
): Map<string, RangingRecordResponse> {
  const latestByTargetId = new Map<string, RangingRecordResponse>();

  for (const record of records) {
    const counterpart =
      record.listener_node.id === sourceNodeId
        ? record.initiator_node
        : record.listener_node;

    if (!targetNodeIds.has(counterpart.id)) {
      continue;
    }

    const existing = latestByTargetId.get(counterpart.id);
    if (
      !existing ||
      new Date(record.recorded_at) > new Date(existing.recorded_at)
    ) {
      latestByTargetId.set(counterpart.id, record);
    }
  }

  return latestByTargetId;
}

function toRange(
  record: RangingRecordResponse | undefined,
  sourceNodeId: string,
  targetNodeId: string,
): RangeMonitorRange | null {
  if (!record) {
    return null;
  }

  return {
    distance: record.distance,
    recordedAt: record.recorded_at,
    sourceNodeId,
    targetNodeId,
  };
}
