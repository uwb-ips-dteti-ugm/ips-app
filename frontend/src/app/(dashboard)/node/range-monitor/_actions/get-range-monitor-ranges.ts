"use server";

import { fetchLatestRangesByTarget } from "@/lib/utils/ranging-latest";
import { getAuthSession } from "@/lib/auth/session";

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
    const latestByTargetId = await fetchLatestRangesByTarget({
      accessToken: session.accessToken,
      sourceNodeId,
      targetNodeIds,
    });

    return {
      ok: true,
      ranges: targetNodeIds.map((targetNodeId) => ({
        range: latestByTargetId.get(targetNodeId) ?? null,
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
