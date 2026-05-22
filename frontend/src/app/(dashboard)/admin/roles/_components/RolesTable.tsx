import type { ReactNode } from "react";

import type { RoleResponse } from "@/lib/api/role";
import {
  DataTable,
  EmptyTableState,
  RowActions,
  TableBadge,
  TableCell,
  TableHead,
} from "@/shared/components/Table";

type RolesTableProps = {
  renderActions?: (role: RoleResponse) => ReactNode;
  renderDefault?: (role: RoleResponse) => ReactNode;
  roles: RoleResponse[];
};

export function RolesTable({
  renderActions,
  renderDefault,
  roles,
}: RolesTableProps) {
  if (roles.length === 0) {
    return <EmptyTableState message="No roles found." />;
  }

  return (
    <DataTable>
      <thead className="bg-[#EAF6FB] text-xs uppercase text-[#1C4D8D] dark:bg-[#0B1E38] dark:text-[#BDE8F5]">
        <tr>
          <TableHead>Name</TableHead>
          <TableHead>Description</TableHead>
          <TableHead className="text-center">Default</TableHead>
          <TableHead className="text-center">Permissions</TableHead>
          <TableHead>Created</TableHead>
          {renderActions ? (
            <TableHead className="text-center">Actions</TableHead>
          ) : null}
        </tr>
      </thead>
      <tbody>
        {roles.map((role) => (
          <tr
            key={role.id}
            className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
          >
            <TableCell>
              <span className="font-semibold text-[#0F2854] dark:text-white">
                {role.name}
              </span>
            </TableCell>
            <TableCell>{role.description || "No description"}</TableCell>
            <TableCell className="text-center">
              {renderDefault ? renderDefault(role) : <DefaultRoleLabel role={role} />}
            </TableCell>
            <TableCell className="text-center">
              {role.permissions.length}
            </TableCell>
            <TableCell>{formatTimestamp(role.created_at)}</TableCell>
            {renderActions ? (
              <TableCell className="text-center">
                <RowActions>{renderActions(role)}</RowActions>
              </TableCell>
            ) : null}
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}

function DefaultRoleLabel({ role }: { role: RoleResponse }) {
  return role.is_default ? (
    <TableBadge className="border-[#4988C4]/40 bg-[#BDE8F5]/50 text-[#0F2854] dark:text-[#BDE8F5]">
      Default
    </TableBadge>
  ) : (
    "No"
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
