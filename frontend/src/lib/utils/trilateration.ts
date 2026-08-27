// 2D multilateration from >=3 anchors with known (x, y) and a measured
// distance to each. UWB ranges are noisy, so this uses a linear
// least-squares solve (subtract a reference anchor's equation from the
// others) rather than a naive 3-circle intersection, and degrades
// gracefully to more anchors than 3 if they're ever added.

export type AnchorPosition = {
  x: number;
  y: number;
  z: number;
};

export type AnchorReading = AnchorPosition & {
  distance: number;
};

export type Point2D = {
  x: number;
  y: number;
};

// UWB ranges are the straight-line (3D) distance between two radios. Anchors
// mounted at different heights than the tag would otherwise bias the 2D
// solve, so this projects each reading onto the horizontal plane assuming
// the tag is carried at `tagHeight` meters off the floor.
export function toHorizontalDistance(
  reading: AnchorReading,
  tagHeight: number,
): number {
  const heightDelta = reading.z - tagHeight;
  const horizontalSquared = reading.distance ** 2 - heightDelta ** 2;
  return Math.sqrt(Math.max(horizontalSquared, 0));
}

export function solveTrilateration2D(
  readings: AnchorReading[],
  tagHeight: number,
): Point2D | null {
  if (readings.length < 3) {
    return null;
  }

  const reference = readings[0];
  const referenceHorizontal = toHorizontalDistance(reference, tagHeight);

  const rows = readings.slice(1).map((reading) => {
    const horizontal = toHorizontalDistance(reading, tagHeight);
    return {
      a: 2 * (reading.x - reference.x),
      b: 2 * (reading.y - reference.y),
      c:
        referenceHorizontal ** 2 -
        horizontal ** 2 +
        (reading.x ** 2 - reference.x ** 2) +
        (reading.y ** 2 - reference.y ** 2),
    };
  });

  // Normal equations for [x, y]: (AtA) p = Atc
  let ataXX = 0;
  let ataXY = 0;
  let ataYY = 0;
  let atcX = 0;
  let atcY = 0;

  for (const row of rows) {
    ataXX += row.a * row.a;
    ataXY += row.a * row.b;
    ataYY += row.b * row.b;
    atcX += row.a * row.c;
    atcY += row.b * row.c;
  }

  const determinant = ataXX * ataYY - ataXY * ataXY;
  if (Math.abs(determinant) < 1e-9) {
    return null;
  }

  const x = (atcX * ataYY - atcY * ataXY) / determinant;
  const y = (atcY * ataXX - atcX * ataXY) / determinant;

  if (!Number.isFinite(x) || !Number.isFinite(y)) {
    return null;
  }

  return { x, y };
}
