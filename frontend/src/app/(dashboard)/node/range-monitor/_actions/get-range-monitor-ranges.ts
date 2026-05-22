"use server";

import {
  getLatestRangingRecord,
  isRangingRecordData,
  type RecordResponse,
} from "@/lib/api/record";
import { getAuthSession } from "@/lib/auth/session";

export type RangeMonitorRange = {
  distance: number;
  recordedAt: string;
  sourceNodeDeviceId: string;
  targetNodeDeviceId: string;
};

export type RangeMonitorRangeRow = {
  range: RangeMonitorRange | null;
  targetNodeDeviceId: string;
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
  sourceNodeDeviceId,
  targetNodeDeviceIds,
}: {
  sourceNodeDeviceId: string;
  targetNodeDeviceIds: string[];
}): Promise<RangeMonitorRangesActionResult> {
  if (!sourceNodeDeviceId) {
    return {
      error: "Select a node before monitoring ranges.",
      ok: false,
    };
  }

  if (targetNodeDeviceIds.length === 0) {
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
    const ranges = await Promise.all(
      targetNodeDeviceIds.map(async (targetNodeDeviceId) => {
        const [forward, reverse] = await Promise.all([
          getLatestRangingRecord(
            {
              source_node_device_ids: [sourceNodeDeviceId],
              target_node_device_ids: [targetNodeDeviceId],
            },
            { accessToken: session.accessToken },
          ),
          getLatestRangingRecord(
            {
              source_node_device_ids: [targetNodeDeviceId],
              target_node_device_ids: [sourceNodeDeviceId],
            },
            { accessToken: session.accessToken },
          ),
        ]);

        return {
          range: pickLatestRange(forward.data, reverse.data),
          targetNodeDeviceId,
        };
      }),
    );

    return {
      ok: true,
      ranges,
    };
  } catch {
    return {
      error: "The latest ranges could not be loaded. Please try again.",
      ok: false,
    };
  }
}

function pickLatestRange(
  first: RecordResponse | null,
  second: RecordResponse | null,
): RangeMonitorRange | null {
  const ranges = [toRange(first), toRange(second)].filter(
    (range): range is RangeMonitorRange => range !== null,
  );

  ranges.sort(
    (left, right) =>
      new Date(right.recordedAt).getTime() - new Date(left.recordedAt).getTime(),
  );

  return ranges[0] ?? null;
}

function toRange(record: RecordResponse | null): RangeMonitorRange | null {
  if (!record || record.label !== "ranging" || !isRangingRecordData(record.data)) {
    return null;
  }

  return {
    distance: record.data.distance,
    recordedAt: record.recorded_at,
    sourceNodeDeviceId: record.data.source_node_device_id,
    targetNodeDeviceId: record.data.target_node_device_id,
  };
}
