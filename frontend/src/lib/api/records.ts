import { apiBaseUrl, authenticatedFetch } from "@/lib/api/client";

export type RangingRecord = {
  id: string | null;
  label: "ranging";
  data: {
    source_node_device_id: string | null;
    target_node_device_id: string | null;
    distance: number | null;
  };
  metadata: Record<string, unknown>;
  recorded_at: string;
  created_at: string;
};

type RecordsResponse = {
  data: RangingRecord[];
};

export async function fetchRangingRecordsByPair({
  accessToken,
  sourceNodeDeviceId,
  targetNodeDeviceId,
  start,
  end,
}: {
  accessToken: string;
  sourceNodeDeviceId: string;
  targetNodeDeviceId: string;
  start: Date;
  end: Date;
}): Promise<RangingRecord[]> {
  const response = await authenticatedFetch(
    accessToken,
    new URL("/records/query", apiBaseUrl),
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        label: "ranging",
        interval_field: "recorded_at",
        start: start.toISOString(),
        end: end.toISOString(),
        source_node_device_ids: [sourceNodeDeviceId, targetNodeDeviceId],
        target_node_device_ids: [sourceNodeDeviceId, targetNodeDeviceId],
      }),
    },
  );

  if (!response.ok) {
    throw new Error("Failed to fetch ranging records.");
  }

  const body = (await response.json()) as RecordsResponse;
  return body.data.filter((record) =>
    isRecordForPair(record, sourceNodeDeviceId, targetNodeDeviceId),
  );
}

export function getLatestRangingRecord(
  records: RangingRecord[],
): RangingRecord | null {
  return [...records].sort((left, right) => {
    return (
      new Date(right.recorded_at).getTime() -
      new Date(left.recorded_at).getTime()
    );
  })[0] ?? null;
}

function isRecordForPair(
  record: RangingRecord,
  sourceNodeDeviceId: string,
  targetNodeDeviceId: string,
) {
  const source = record.data.source_node_device_id;
  const target = record.data.target_node_device_id;
  return (
    (source === sourceNodeDeviceId && target === targetNodeDeviceId) ||
    (source === targetNodeDeviceId && target === sourceNodeDeviceId)
  );
}
