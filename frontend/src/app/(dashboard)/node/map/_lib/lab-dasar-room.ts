import type { Point2D } from "@/lib/utils/trilateration";

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

export const DEFAULT_TAG_HEIGHT_M = 1.0;
