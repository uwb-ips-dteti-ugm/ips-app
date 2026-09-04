// Shared 2D/3D point types for the map feature. The actual trilateration
// math now runs server-side (backend `/position/compute`) -- see
// `application/position/trilateration.py`.

export type AnchorPosition = {
  x: number;
  y: number;
  z: number;
};

export type Point2D = {
  x: number;
  y: number;
};
