"use server";

import { getAuthSession } from "@/lib/auth/session";
import { fetchLatestRangesByTarget } from "@/lib/utils/ranging-latest";
import {
  solveTrilateration2D,
  type AnchorReading,
  type Point2D,
} from "@/lib/utils/trilateration";

import { LAB_DASAR_ANCHORS } from "../_lib/lab-dasar-room";
import type { MapAnchorNode } from "../_lib/get-map-page-data";

export type AnchorRangeReading = {
  anchorLabel: string;
  distance: number | null;
  recordedAt: string | null;
};

export type GetTagPositionResult =
  | {
      ok: true;
      position: Point2D | null;
      readings: AnchorRangeReading[];
    }
  | {
      error: string;
      ok: false;
    };

export async function getTagPositionAction({
  anchors,
  tagHeight,
  tagNodeId,
}: {
  anchors: MapAnchorNode[];
  tagHeight: number;
  tagNodeId: string;
}): Promise<GetTagPositionResult> {
  if (!tagNodeId) {
    return { error: "Select a mobile node to track.", ok: false };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again to view the map.",
      ok: false,
    };
  }

  try {
    const latestByAnchorId = await fetchLatestRangesByTarget({
      accessToken: session.accessToken,
      sourceNodeId: tagNodeId,
      targetNodeIds: anchors.map((anchor) => anchor.id),
    });

    const readings: AnchorRangeReading[] = anchors.map((anchor) => {
      const range = latestByAnchorId.get(anchor.id);
      return {
        anchorLabel: anchor.label,
        distance: range?.distance ?? null,
        recordedAt: range?.recordedAt ?? null,
      };
    });

    const trilaterationInputs: AnchorReading[] = anchors.flatMap((anchor) => {
      const range = latestByAnchorId.get(anchor.id);
      if (!range) {
        return [];
      }

      return [
        {
          x: anchor.x,
          y: anchor.y,
          z: anchor.z,
          distance: range.distance,
        },
      ];
    });

    const position =
      trilaterationInputs.length >= LAB_DASAR_ANCHORS.length
        ? solveTrilateration2D(trilaterationInputs, tagHeight)
        : null;

    return { ok: true, position, readings };
  } catch {
    return {
      error: "The mobile node's position could not be loaded. Please try again.",
      ok: false,
    };
  }
}
