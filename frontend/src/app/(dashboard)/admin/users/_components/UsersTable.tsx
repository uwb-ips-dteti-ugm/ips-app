import type { ReactNode } from "react";

import type { UserResponse, UserStatus } from "@/lib/api/user";
import {
  DataTable,
  EmptyTableState,
  RowActions,
  TableBadge,
  TableCell,
  TableHead,
} from "@/shared/components/Table";

import type { UserRoleFilterOption } from "../_lib/get-users-page-data";
import { UserRoleSelect, UserStatusSelect } from "./UserTableSelect";

type UsersTableProps = {
  canManageUsers: boolean;
  renderActions?: (user: UserResponse) => ReactNode;
  roles: UserRoleFilterOption[];
  users: UserResponse[];
};

export function UsersTable({
  canManageUsers,
  renderActions,
  roles,
  users,
}: UsersTableProps) {
  if (users.length === 0) {
    return <EmptyTableState message="No users found." />;
  }

  return (
    <DataTable>
      <thead className="bg-[#EAF6FB] text-xs uppercase text-[#1C4D8D] dark:bg-[#0B1E38] dark:text-[#BDE8F5]">
        <tr>
          <TableHead>Name</TableHead>
          <TableHead>Username</TableHead>
          <TableHead className="text-center">Role</TableHead>
          <TableHead className="text-center">Status</TableHead>
          <TableHead>Created</TableHead>
          {renderActions ? (
            <TableHead className="text-center">Actions</TableHead>
          ) : null}
        </tr>
      </thead>
      <tbody>
        {users.map((user) => (
          <tr
            key={user.id}
            className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
          >
            <TableCell>
              <div className="max-w-72">
                <div className="truncate font-semibold text-[#0F2854] dark:text-white">
                  {user.name}
                </div>
                {user.bio ? (
                  <div className="truncate text-xs text-[#4988C4] dark:text-[#BDE8F5]">
                    {user.bio}
                  </div>
                ) : null}
              </div>
            </TableCell>
            <TableCell>{user.username ?? "No username"}</TableCell>
            <TableCell className="text-center">
              {canManageUsers && roles.length > 0 ? (
                <UserRoleSelect roles={roles} user={user} />
              ) : (
                user.role.name
              )}
            </TableCell>
            <TableCell className="text-center">
              {canManageUsers ? (
                <UserStatusSelect user={user} />
              ) : (
                <UserStatusBadge status={user.status} />
              )}
            </TableCell>
            <TableCell>{formatTimestamp(user.created_at)}</TableCell>
            {renderActions ? (
              <TableCell className="text-center">
                <RowActions>{renderActions(user)}</RowActions>
              </TableCell>
            ) : null}
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}

function UserStatusBadge({ status }: { status: UserStatus }) {
  const className = {
    active:
      "border-[#4988C4]/40 bg-[#BDE8F5]/50 text-[#0F2854] dark:text-[#BDE8F5]",
    banned:
      "border-rose-500/40 bg-rose-500/10 text-rose-700 dark:text-rose-300",
    suspended:
      "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300",
  }[status];

  return <TableBadge className={className}>{formatLabel(status)}</TableBadge>;
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

function formatLabel(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
