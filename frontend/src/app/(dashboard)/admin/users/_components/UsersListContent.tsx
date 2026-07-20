"use client";

import Image from "next/image";
import { useState } from "react";

import type { UserResponse } from "@/lib/api/user";
import editIcon from "@/shared/assets/EditIcon.svg";
import infoIcon from "@/shared/assets/InfoIcon.svg";
import keyIcon from "@/shared/assets/KeyIcon.svg";
import plusIcon from "@/shared/assets/PlusIcon.svg";
import trashIcon from "@/shared/assets/TrashIcon.svg";
import {
  IconActionButton,
  TableFrame,
  TableLoadingOverlay,
  TableViewport,
} from "@/shared/components/Table";

import type { UserRoleFilterOption } from "../_lib/get-users-page-data";
import type { UsersListState } from "../_lib/users-list-state";
import {
  AddUserModal,
  DeleteUserModal,
  EditUserModal,
  InfoUserModal,
  ResetUserPasswordModal,
} from "./UserActionModals";
import { UsersFilterBar } from "./UsersFilterBar";
import { UsersPagination } from "./UsersPagination";
import { UsersTable } from "./UsersTable";

type UsersListContentProps = {
  canDeleteUsers: boolean;
  canManageUsers: boolean;
  canRegisterUsers: boolean;
  canResetUserPasswords: boolean;
  limit: number;
  roles: UserRoleFilterOption[];
  state: UsersListState;
  total: number;
  users: UserResponse[];
};

type ActiveUserModal =
  | {
      type: "add";
    }
  | {
      type: "delete";
      user: UserResponse;
    }
  | {
      type: "edit";
      user: UserResponse;
    }
  | {
      type: "info";
      user: UserResponse;
    }
  | {
      type: "reset-password";
      user: UserResponse;
    }
  | null;

export function UsersListContent({
  canDeleteUsers,
  canManageUsers,
  canRegisterUsers,
  canResetUserPasswords,
  limit,
  roles,
  state,
  total,
  users,
}: UsersListContentProps) {
  const [activeModal, setActiveModal] = useState<ActiveUserModal>(null);
  const [isTableLoading, setIsTableLoading] = useState(false);

  return (
    <>
      <UsersFilterBar
        actions={
          canRegisterUsers ? (
            <button
              type="button"
              disabled={roles.length === 0}
              title={roles.length === 0 ? "No role available" : "Add user"}
              onClick={() => setActiveModal({ type: "add" })}
              className="inline-flex h-10 items-center justify-center gap-2 whitespace-nowrap rounded-md bg-[#0F2854] px-4 text-sm font-semibold text-white transition hover:bg-[#1C4D8D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#4988C4] dark:hover:bg-[#1C4D8D]"
            >
              <Image
                src={plusIcon}
                alt=""
                width={16}
                height={16}
                className="shrink-0"
              />
              Add User
            </button>
          ) : null
        }
        filters={state}
        roles={roles}
        onTableLoadingChange={setIsTableLoading}
      />

      <TableFrame>
        <TableViewport>
          <UsersTable
            canManageUsers={canManageUsers}
            renderActions={(user) => (
              <>
                <IconActionButton
                  icon={infoIcon}
                  label="Info"
                  onClick={() => setActiveModal({ type: "info", user })}
                />
                {canManageUsers ? (
                  <IconActionButton
                    icon={editIcon}
                    label="Edit"
                    onClick={() => setActiveModal({ type: "edit", user })}
                  />
                ) : null}
                {canResetUserPasswords ? (
                  <IconActionButton
                    icon={keyIcon}
                    label="Change password"
                    onClick={() =>
                      setActiveModal({ type: "reset-password", user })
                    }
                  />
                ) : null}
                {canDeleteUsers ? (
                  <IconActionButton
                    icon={trashIcon}
                    label="Delete"
                    onClick={() => setActiveModal({ type: "delete", user })}
                    variant="danger"
                  />
                ) : null}
              </>
            )}
            roles={roles}
            users={users}
          />
          {isTableLoading ? (
            <TableLoadingOverlay label="Loading users" />
          ) : null}
        </TableViewport>

        <UsersPagination
          itemCount={users.length}
          limit={limit}
          onTableLoadingChange={setIsTableLoading}
          page={state.page}
          total={total}
        />
      </TableFrame>

      {activeModal?.type === "info" ? (
        <InfoUserModal
          user={activeModal.user}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "add" ? (
        <AddUserModal roles={roles} onClose={() => setActiveModal(null)} />
      ) : null}
      {activeModal?.type === "edit" ? (
        <EditUserModal
          user={activeModal.user}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "reset-password" ? (
        <ResetUserPasswordModal
          user={activeModal.user}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "delete" ? (
        <DeleteUserModal
          user={activeModal.user}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
    </>
  );
}
