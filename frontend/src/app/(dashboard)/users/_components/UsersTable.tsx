"use client";

import { formatDate, formatLabel } from "@/lib/format";
import editIcon from "@/shared/assets/EditIcon.svg";
import infoIcon from "@/shared/assets/InfoIcon.svg";
import trashIcon from "@/shared/assets/TrashIcon.svg";
import {
  DataTable,
  EmptyTableState,
  IconActionButton,
  RowActions,
  TableBadge,
  TableCell,
  TableHead,
} from "@/shared/components/Table";

export type UserState = "online" | "offline" | "away" | "dnd";
export type UserStatus = "active" | "suspended" | "banned";

export type UserListItem = {
  id: string;
  name: string;
  username: string | null;
  bio: string;
  state: UserState;
  status: UserStatus;
  role: {
    id: string;
    name: string;
    description: string;
    is_default: boolean;
  } | null;
  last_signed_in_at: string | null;
  last_refreshed_at: string | null;
  last_activity_at: string | null;
  created_at: string;
  updated_at: string | null;
  version: number;
};

type UsersTableProps = {
  users: UserListItem[];
  canManageUsers: boolean;
  canDeleteUsers: boolean;
  onViewUser: (user: UserListItem) => void;
  onEditUser: (user: UserListItem) => void;
  onDeleteUser: (user: UserListItem) => void;
};

export function UsersTable({
  users,
  canManageUsers,
  canDeleteUsers,
  onViewUser,
  onEditUser,
  onDeleteUser,
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
          <TableHead>Role</TableHead>
          <TableHead>State</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Last Activity</TableHead>
          <TableHead>Actions</TableHead>
        </tr>
      </thead>
      <tbody>
        {users.map((user) => (
          <tr
            key={user.id}
            className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
          >
            <TableCell>
              <div className="max-w-64">
                <div className="truncate font-semibold text-[#0F2854] dark:text-white">
                  {user.name}
                </div>
                {user.bio && (
                  <div className="truncate text-xs text-[#4988C4] dark:text-[#BDE8F5]">
                    {user.bio}
                  </div>
                )}
              </div>
            </TableCell>
            <TableCell>{user.username ?? "No username"}</TableCell>
            <TableCell className="text-center">
              {user.role?.name ?? "No role"}
            </TableCell>
            <TableCell className="text-center">
              <UserStateBadge state={user.state} />
            </TableCell>
            <TableCell className="text-center">
              <UserStatusBadge status={user.status} />
            </TableCell>
            <TableCell>{formatDate(user.last_activity_at)}</TableCell>
            <TableCell className="text-center">
              <RowActions>
                <IconActionButton
                  icon={infoIcon}
                  label="Info"
                  onClick={() => onViewUser(user)}
                />
                {canManageUsers && (
                  <IconActionButton
                    icon={editIcon}
                    label="Edit"
                    onClick={() => onEditUser(user)}
                  />
                )}
                {canDeleteUsers && (
                  <IconActionButton
                    icon={trashIcon}
                    label="Delete"
                    onClick={() => onDeleteUser(user)}
                    variant="danger"
                  />
                )}
              </RowActions>
            </TableCell>
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}

function UserStateBadge({ state }: { state: UserState }) {
  const className = {
    online: "border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
    offline: "border-slate-400/40 bg-slate-400/10 text-slate-600 dark:text-slate-300",
    away: "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300",
    dnd: "border-rose-500/40 bg-rose-500/10 text-rose-700 dark:text-rose-300",
  }[state];

  return <TableBadge className={className}>{formatLabel(state)}</TableBadge>;
}

function UserStatusBadge({ status }: { status: UserStatus }) {
  const className = {
    active: "border-[#4988C4]/40 bg-[#BDE8F5]/50 text-[#0F2854] dark:text-[#BDE8F5]",
    suspended: "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300",
    banned: "border-rose-500/40 bg-rose-500/10 text-rose-700 dark:text-rose-300",
  }[status];

  return <TableBadge className={className}>{formatLabel(status)}</TableBadge>;
}
