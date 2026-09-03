import math
from typing import List, NamedTuple, Optional, Sequence

# 2D multilateration from >=3 anchors with known (x, y, z) and a measured
# distance to each. UWB ranges are noisy, so this uses a linear
# least-squares solve (subtract a reference anchor's equation from the
# others) rather than a naive 3-circle intersection, and it degrades
# gracefully to more anchors than 3 if they're ever added.

MIN_ANCHORS = 3


class AnchorReading(NamedTuple):
    x: float
    y: float
    z: float
    distance: float


class Point2D(NamedTuple):
    x: float
    y: float


def to_horizontal_distance(reading: AnchorReading, tag_height: float) -> float:
    """UWB ranges are the straight-line (3D) distance between two radios. Anchors
    mounted at a different height than the tag would otherwise bias the 2D
    solve, so this projects each reading onto the horizontal plane assuming
    the tag is carried at `tag_height` meters off the floor."""
    height_delta = reading.z - tag_height
    horizontal_squared = reading.distance**2 - height_delta**2
    return math.sqrt(max(horizontal_squared, 0.0))


def solve_trilateration_2d(
    readings: Sequence[AnchorReading], tag_height: float
) -> Optional[Point2D]:
    if len(readings) < MIN_ANCHORS:
        return None

    reference = readings[0]
    reference_horizontal = to_horizontal_distance(reference, tag_height)

    rows: List[tuple[float, float, float]] = []
    for reading in readings[1:]:
        horizontal = to_horizontal_distance(reading, tag_height)
        a = 2 * (reading.x - reference.x)
        b = 2 * (reading.y - reference.y)
        c = (
            reference_horizontal**2
            - horizontal**2
            + (reading.x**2 - reference.x**2)
            + (reading.y**2 - reference.y**2)
        )
        rows.append((a, b, c))

    # Normal equations for [x, y]: (AtA) p = Atc
    ata_xx = sum(a * a for a, _, _ in rows)
    ata_xy = sum(a * b for a, b, _ in rows)
    ata_yy = sum(b * b for _, b, _ in rows)
    atc_x = sum(a * c for a, _, c in rows)
    atc_y = sum(b * c for _, b, c in rows)

    determinant = ata_xx * ata_yy - ata_xy * ata_xy
    if abs(determinant) < 1e-9:
        return None

    x = (atc_x * ata_yy - atc_y * ata_xy) / determinant
    y = (atc_y * ata_xx - atc_x * ata_xy) / determinant

    if not (math.isfinite(x) and math.isfinite(y)):
        return None

    return Point2D(x=x, y=y)
