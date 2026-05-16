export function getStringParam(value: string | string[] | undefined) {
  if (Array.isArray(value)) {
    return value[0] ?? "";
  }

  return value ?? "";
}

export function getPageParam(value: string | string[] | undefined) {
  const page = Number.parseInt(getStringParam(value), 10);
  return Number.isFinite(page) && page >= 0 ? page : 0;
}

export function getLimitParam(
  value: string | string[] | undefined,
  allowedLimits = [10, 20, 50],
) {
  const limit = Number.parseInt(getStringParam(value), 10);
  return allowedLimits.includes(limit) ? limit : allowedLimits[0];
}
