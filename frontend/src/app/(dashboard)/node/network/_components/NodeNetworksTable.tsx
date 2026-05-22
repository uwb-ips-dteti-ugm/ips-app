import type { ReactNode } from "react";

import type { NodeNetworkResponse } from "@/lib/api/node-network";
import {
  DataTable,
  EmptyTableState,
  RowActions,
  TableCell,
  TableHead,
} from "@/shared/components/Table";

type NodeNetworksTableProps = {
  nodeNetworks: NodeNetworkResponse[];
  renderActions?: (nodeNetwork: NodeNetworkResponse) => ReactNode;
};

export function NodeNetworksTable({
  nodeNetworks,
  renderActions,
}: NodeNetworksTableProps) {
  if (nodeNetworks.length === 0) {
    return <EmptyTableState message="No node networks found." />;
  }

  return (
    <DataTable>
      <thead className="bg-[#EAF6FB] text-xs uppercase text-[#1C4D8D] dark:bg-[#0B1E38] dark:text-[#BDE8F5]">
        <tr>
          <TableHead>Name</TableHead>
          <TableHead>PAN ID Hex</TableHead>
          <TableHead>PAN ID Integer</TableHead>
          <TableHead>Description</TableHead>
          <TableHead>Created</TableHead>
          {renderActions ? (
            <TableHead className="text-center">Actions</TableHead>
          ) : null}
        </tr>
      </thead>
      <tbody>
        {nodeNetworks.map((nodeNetwork) => (
          <tr
            key={nodeNetwork.id}
            className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
          >
            <TableCell>
              <span className="font-semibold text-[#0F2854] dark:text-white">
                {nodeNetwork.name}
              </span>
            </TableCell>
            <TableCell>
              <span className="font-semibold text-[#0F2854] dark:text-white">
                {formatPanId(nodeNetwork.pan_id)}
              </span>
            </TableCell>
            <TableCell>{nodeNetwork.pan_id}</TableCell>
            <TableCell>{nodeNetwork.description || "No description"}</TableCell>
            <TableCell>{formatTimestamp(nodeNetwork.created_at)}</TableCell>
            {renderActions ? (
              <TableCell className="text-center">
                <RowActions>{renderActions(nodeNetwork)}</RowActions>
              </TableCell>
            ) : null}
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}

export function formatPanId(value: number): string {
  return `0x${value.toString(16).padStart(4, "0").toUpperCase()}`;
}

function formatTimestamp(value: string): string {
  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(timestamp);
}
