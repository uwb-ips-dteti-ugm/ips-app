import type { ReactNode } from "react";

import type { NodeResponse, NodeStatus } from "@/lib/api/node";
import {
  DataTable,
  EmptyTableState,
  RowActions,
  TableBadge,
  TableCell,
  TableHead,
} from "@/shared/components/Table";

type NodesTableProps = {
  nodes: NodeResponse[];
  renderActions?: (node: NodeResponse) => ReactNode;
};

export function NodesTable({ nodes, renderActions }: NodesTableProps) {
  if (nodes.length === 0) {
    return <EmptyTableState message="No nodes found." />;
  }

  return (
    <DataTable>
      <thead className="bg-[#EAF6FB] text-xs uppercase text-[#1C4D8D] dark:bg-[#0B1E38] dark:text-[#BDE8F5]">
        <tr>
          <TableHead>Node</TableHead>
          <TableHead className="text-center">Connection</TableHead>
          <TableHead>Device ID</TableHead>
          <TableHead className="text-center">Status</TableHead>
          <TableHead>Network</TableHead>
          <TableHead>Address</TableHead>
          <TableHead>Last Seen</TableHead>
          {renderActions ? (
            <TableHead className="text-center">Actions</TableHead>
          ) : null}
        </tr>
      </thead>
      <tbody>
        {nodes.map((node) => (
          <tr
            key={node.id}
            className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
          >
            <TableCell>
              <div className="max-w-72">
                <div className="truncate font-semibold text-[#0F2854] dark:text-white">
                  {node.name}
                </div>
              </div>
            </TableCell>
            <TableCell className="text-center">
              <NodeConnectionBadge node={node} />
            </TableCell>
            <TableCell>{node.device_id}</TableCell>
            <TableCell className="text-center">
              <NodeStatusBadge status={node.status} />
            </TableCell>
            <TableCell>
              {node.network ? node.network.name : "Unassigned"}
            </TableCell>
            <TableCell>{formatAddress(node.address)}</TableCell>
            <TableCell>{formatTimestamp(node.last_seen_at, "Never")}</TableCell>
            {renderActions ? (
              <TableCell className="text-center">
                <RowActions>{renderActions(node)}</RowActions>
              </TableCell>
            ) : null}
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}

function NodeConnectionBadge({ node }: { node: NodeResponse }) {
  const status = getConnectionStatus(node);
  const className = {
    never:
      "border-slate-500/40 bg-slate-500/10 text-slate-700 dark:text-slate-300",
    offline: "border-rose-500/40 bg-rose-500/10 text-rose-700 dark:text-rose-300",
    online:
      "border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
  }[status];

  return (
    <TableBadge className={className}>{formatConnectionStatus(status)}</TableBadge>
  );
}

export function NodeStatusBadge({ status }: { status: NodeStatus }) {
  const className = {
    approved:
      "border-[#4988C4]/40 bg-[#BDE8F5]/50 text-[#0F2854] dark:text-[#BDE8F5]",
    pending:
      "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300",
    suspended:
      "border-slate-500/40 bg-slate-500/10 text-slate-700 dark:text-slate-300",
  }[status];

  return <TableBadge className={className}>{formatLabel(status)}</TableBadge>;
}

export function formatAddress(value: number | null): string {
  return value === null ? "Unassigned" : `${formatUwbValue(value)} (${value})`;
}

export function formatTimestamp(value: string | null, fallback: string): string {
  if (!value) {
    return fallback;
  }

  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(timestamp);
}

function getConnectionStatus(
  node: NodeResponse,
): "never" | "offline" | "online" {
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

function formatUwbValue(value: number): string {
  return `0x${value.toString(16).padStart(4, "0").toUpperCase()}`;
}

function formatConnectionStatus(value: "never" | "offline" | "online"): string {
  if (value === "never") {
    return "Never";
  }

  return formatLabel(value);
}

function formatLabel(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
