"use client";

import { useCallback, useState } from "react";

import {
  DeleteUserModal,
  EditUserModal,
  InfoUserModal,
  RegisterUserModal,
} from "./UserModals";
import { UsersPagination } from "./UsersPagination";
import {
  type UserRoleFilterOption,
  type UserStateFilterValue,
  type UserStatusFilterValue,
  UsersSearchForm,
} from "./UsersSearchForm";
import { type UserListItem, UsersTable } from "./UsersTable";
import { TableLoadingOverlay } from "@/shared/components/Table";

type UsersPageContentProps = {
  users: UserListItem[];
  meta: {
    page: number;
    limit: number;
    total: number;
  };
  filters: {
    search: string;
    roleId: string;
    state: UserStateFilterValue;
    status: UserStatusFilterValue;
  };
  roles: UserRoleFilterOption[];
  canRegisterUsers: boolean;
  canManageUsers: boolean;
  canDeleteUsers: boolean;
};

type ActiveUserModal =
  | { type: "register" }
  | { type: "info"; user: UserListItem }
  | { type: "edit"; user: UserListItem }
  | { type: "delete"; user: UserListItem }
  | null;

export function UsersPageContent({
  users,
  meta,
  filters,
  roles,
  canRegisterUsers,
  canManageUsers,
  canDeleteUsers,
}: UsersPageContentProps) {
  const [isTableLoading, setIsTableLoading] = useState(false);
  const [activeModal, setActiveModal] = useState<ActiveUserModal>(null);
  const closeModal = useCallback(() => setActiveModal(null), []);

  return (
    <>
      <div>
        <UsersSearchForm
          search={filters.search}
          limit={meta.limit}
          roleId={filters.roleId}
          state={filters.state}
          status={filters.status}
          roles={roles}
          canRegisterUsers={canRegisterUsers}
          onRegisterUser={() => setActiveModal({ type: "register" })}
          onTableLoadingChange={setIsTableLoading}
        />
      </div>

      <section className="overflow-hidden rounded-md border border-[#D9EEF7] bg-white dark:border-[#1C4D8D] dark:bg-[#07111F]">
        <div className="relative">
          <UsersTable
            users={users}
            canManageUsers={canManageUsers}
            canDeleteUsers={canDeleteUsers}
            onViewUser={(user) => setActiveModal({ type: "info", user })}
            onEditUser={(user) => setActiveModal({ type: "edit", user })}
            onDeleteUser={(user) => setActiveModal({ type: "delete", user })}
          />
          {isTableLoading && <TableLoadingOverlay label="Loading users" />}
        </div>
        <UsersPagination
          page={meta.page}
          limit={meta.limit}
          total={meta.total}
          search={filters.search}
          roleId={filters.roleId}
          state={filters.state}
          status={filters.status}
          onTableLoadingChange={setIsTableLoading}
        />
      </section>

      {activeModal?.type === "register" && (
        <RegisterUserModal roles={roles} onClose={closeModal} />
      )}
      {activeModal?.type === "info" && (
        <InfoUserModal user={activeModal.user} onClose={closeModal} />
      )}
      {activeModal?.type === "edit" && (
        <EditUserModal
          user={activeModal.user}
          roles={roles}
          onClose={closeModal}
        />
      )}
      {activeModal?.type === "delete" && (
        <DeleteUserModal user={activeModal.user} onClose={closeModal} />
      )}
    </>
  );
}
