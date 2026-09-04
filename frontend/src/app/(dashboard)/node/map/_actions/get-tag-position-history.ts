"use server";

import { getPositionRecords } from "@/lib/api/position";
import { isApiError } from "@/lib/api/client";
import { getAuthSession } from "@/lib/auth/session";
import type { Point2D } from "@/lib/utils/trilateration";

export type GetTagPositionHistoryResult =
  | {
      ok: true;
      points: Point2D[];
    }
  | {
      error: string;
      ok: false;
    };

export async function getTagPositionHistoryAction({
  since,
  tagNodeId,
}: {
  since: Date;
  tagNodeId: string;
}): Promise<GetTagPositionHistoryResult> {
  if (!tagNodeId) {
    return { ok: true, points: [] };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again to view history.",
      ok: false,
    };
  }

  try {
    const records = await getPositionRecords(
      {
        end: new Date().toISOString(),
        start: since.toISOString(),
        tag_node_id: tagNodeId,
      },
      { accessToken: session.accessToken },
    );

    return {
      ok: true,
      points: records.map((record) => ({ x: record.x, y: record.y })),
    };
  } catch (error) {
    return {
      error: isApiError(error)
        ? error.message
        : "The position history could not be loaded.",
      ok: false,
    };
  }
}
