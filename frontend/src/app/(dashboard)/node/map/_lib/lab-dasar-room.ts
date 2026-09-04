import type { AnchorPosition, Point2D } from "@/lib/utils/trilateration";

// Surveyed by hand with a 10m ruler, piece by piece along the walls
// (2026-08-27). The room isn't rectangular: the left wall has two shallow
// jogs and the top wall has two structural pillars protruding into the
// room (the notches around x=7.73-8.18 and x=14.93-15.38). Traced from the
// origin up the left wall, then right along the top wall, ending at the
// top-right corner -- the right and bottom walls are assumed straight and
// are closed below using the full-span ruler measurement (22.39m), since
// they weren't independently surveyed.
const SURVEYED_BOUNDARY: Point2D[] = [
  { x: 0, y: 0 },
  { x: 0, y: 4.47 },
  { x: 1.09, y: 4.47 },
  { x: 1.09, y: 4.92 },
  { x: 0, y: 4.92 },
  { x: 0, y: 8.29 },
  { x: 0.7, y: 8.29 },
  { x: 0.7, y: 11.54 },
  { x: 0.99, y: 11.54 },
  { x: 0.99, y: 12.04 },
  { x: 4.38, y: 12.04 },
  { x: 4.38, y: 12.66 },
  { x: 7.73, y: 12.66 },
  { x: 7.73, y: 11.15 },
  { x: 8.18, y: 11.15 },
  { x: 8.18, y: 12.66 },
  { x: 14.93, y: 12.66 },
  { x: 14.93, y: 11.15 },
  { x: 15.38, y: 11.15 },
  { x: 15.38, y: 12.66 },
  { x: 22.38, y: 12.66 },
];

const FULL_WIDTH_M = 22.39;

export const LAB_DASAR_ROOM_POLYGON: Point2D[] = [
  ...SURVEYED_BOUNDARY,
  { x: FULL_WIDTH_M, y: 0 },
];

export const LAB_DASAR_BOUNDS = {
  width: FULL_WIDTH_M,
  height: 12.66,
};

export type LabDasarAnchorConfig = AnchorPosition & {
  deviceId: string;
  label: string;
};

// device_id -> surveyed anchor position (meters, z = height off the floor).
// Anchors are fixed once mounted, so this is a static config rather than
// something edited at runtime.
export const LAB_DASAR_ANCHORS: LabDasarAnchorConfig[] = [
  { deviceId: "083A8D3E19B0", label: "UWB Labdas 1", x: 0.0, y: 0.0, z: 1.38 },
  { deviceId: "4022D8066694", label: "UWB Labdas 2", x: 4.44, y: 4.0, z: 0.76 },
  { deviceId: "4022D807D460", label: "UWB Labdas 3", x: 1.35, y: 6.85, z: 0.75 },
];

export const DEFAULT_TAG_HEIGHT_M = 1.0;
