export type NodeConnectionStatus = "never" | "offline" | "online";

export function getNodeConnectionStatus(node: {
  last_connected_at: string | null;
  last_disconnected_at: string | null;
}): NodeConnectionStatus {
  const connectedAt = parseTimestamp(node.last_connected_at);
  if (connectedAt === null) {
    return "never";
  }

  const disconnectedAt = parseTimestamp(node.last_disconnected_at);
  if (disconnectedAt === null) {
    return "online";
  }

  return connectedAt > disconnectedAt ? "online" : "offline";
}

function parseTimestamp(value: string | null): number | null {
  if (!value) {
    return null;
  }

  const timestamp = new Date(value).getTime();
  return Number.isNaN(timestamp) ? null : timestamp;
}
