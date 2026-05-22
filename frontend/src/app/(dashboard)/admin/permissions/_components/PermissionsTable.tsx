import type { ReactNode } from "react";

import type { PermissionResponse } from "@/lib/api/permission";
import {
  DataTable,
  EmptyTableState,
  RowActions,
  TableCell,
  TableHead,
} from "@/shared/components/Table";

type PermissionsTableProps = {
  permissions: PermissionResponse[];
  renderActions?: (permission: PermissionResponse) => ReactNode;
};

export function PermissionsTable({
  permissions,
  renderActions,
}: PermissionsTableProps) {
  if (permissions.length === 0) {
    return <EmptyTableState message="No permissions found." />;
  }

  return (
    <DataTable>
      <thead className="bg-[#EAF6FB] text-xs uppercase text-[#1C4D8D] dark:bg-[#0B1E38] dark:text-[#BDE8F5]">
        <tr>
          <TableHead>Name</TableHead>
          <TableHead>Description</TableHead>
          <TableHead>Created</TableHead>
          {renderActions ? (
            <TableHead className="text-center">Actions</TableHead>
          ) : null}
        </tr>
      </thead>
      <tbody>
        {permissions.map((permission) => (
          <tr
            key={permission.id}
            className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
          >
            <TableCell>
              <span className="font-semibold text-[#0F2854] dark:text-white">
                {permission.name}
              </span>
            </TableCell>
            <TableCell>{permission.description || "No description"}</TableCell>
            <TableCell>{formatTimestamp(permission.created_at)}</TableCell>
            {renderActions ? (
              <TableCell className="text-center">
                <RowActions>{renderActions(permission)}</RowActions>
              </TableCell>
            ) : null}
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
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
