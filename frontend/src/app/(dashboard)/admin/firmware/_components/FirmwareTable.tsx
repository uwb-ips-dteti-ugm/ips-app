import type { ReactNode } from "react";

import type { FirmwareResponse } from "@/lib/api/firmware";
import {
  DataTable,
  EmptyTableState,
  RowActions,
  TableCell,
  TableHead,
} from "@/shared/components/Table";

type FirmwareTableProps = {
  firmwares: FirmwareResponse[];
  renderActions?: (firmware: FirmwareResponse) => ReactNode;
};

export function FirmwareTable({ firmwares, renderActions }: FirmwareTableProps) {
  if (firmwares.length === 0) {
    return <EmptyTableState message="No firmware uploaded yet." />;
  }

  return (
    <DataTable>
      <thead className="bg-[#EAF6FB] text-xs uppercase text-[#1C4D8D] dark:bg-[#0B1E38] dark:text-[#BDE8F5]">
        <tr>
          <TableHead>Version</TableHead>
          <TableHead>Board Variant</TableHead>
          <TableHead>Size</TableHead>
          <TableHead>Checksum</TableHead>
          <TableHead>Uploaded</TableHead>
          {renderActions ? <TableHead className="text-center">Actions</TableHead> : null}
        </tr>
      </thead>
      <tbody>
        {firmwares.map((firmware) => (
          <tr
            key={firmware.id}
            className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
          >
            <TableCell className="font-semibold text-[#0F2854] dark:text-white">
              {firmware.version}
            </TableCell>
            <TableCell>{firmware.board_variant}</TableCell>
            <TableCell>{formatSize(firmware.size)}</TableCell>
            <TableCell className="font-mono text-xs">
              {firmware.checksum.slice(0, 12)}…
            </TableCell>
            <TableCell>{formatTimestamp(firmware.created_at)}</TableCell>
            {renderActions ? (
              <TableCell className="text-center">
                <RowActions>{renderActions(firmware)}</RowActions>
              </TableCell>
            ) : null}
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  const kb = bytes / 1024;
  if (kb < 1024) {
    return `${kb.toFixed(1)} KB`;
  }
  return `${(kb / 1024).toFixed(2)} MB`;
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
