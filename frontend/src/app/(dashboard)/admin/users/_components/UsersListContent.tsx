"use client";

import Image from "next/image";
import { useState } from "react";

import type { PaginationMeta } from "@/lib/api/common";
import type { UserResponse } from "@/lib/api/user";
import infoIcon from "@/shared/assets/InfoIcon.svg";
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
  InfoUserModal,
} from "./UserActionModals";
import { UsersFilterBar } from "./UsersFilterBar";
import { UsersPagination } from "./UsersPagination";
import { UsersTable } from "./UsersTable";

type UsersListContentProps = {
  canDeleteUsers: boolean;
  canManageUsers: boolean;
  canRegisterUsers: boolean;
  meta: PaginationMeta;
  roles: UserRoleFilterOption[];
  state: UsersListState;
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
      type: "info";
      user: UserResponse;
    }
  | null;

export function UsersListContent({
  canDeleteUsers,
  canManageUsers,
  canRegisterUsers,
  meta,
  roles,
  state,
  users,
}: UsersListContentProps) {
  const [activeModal, setActiveModal] = useState<ActiveUserModal>(null);
  const [isTableLoading, setIsTableLoading] = useState(false);
  const nextCursorId = users.at(-1)?.id;
  const hasNext = Boolean(nextCursorId) && meta.total > users.length;

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
          cursorId={state.cursorId}
          hasNext={hasNext}
          itemCount={users.length}
          nextCursorId={nextCursorId}
          onTableLoadingChange={setIsTableLoading}
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
      {activeModal?.type === "delete" ? (
        <DeleteUserModal
          user={activeModal.user}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
    </>
  );
}
