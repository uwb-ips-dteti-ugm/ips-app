"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useTransition } from "react";

import type { PaginationMeta } from "@/lib/api/common";
import type { PermissionResponse } from "@/lib/api/permission";
import type { RoleResponse } from "@/lib/api/role";
import editIcon from "@/shared/assets/EditIcon.svg";
import infoIcon from "@/shared/assets/InfoIcon.svg";
import permissionAssignIcon from "@/shared/assets/PermissionAssignIcon.svg";
import plusIcon from "@/shared/assets/PlusIcon.svg";
import trashIcon from "@/shared/assets/TrashIcon.svg";
import {
  IconActionButton,
  TableFrame,
  TableLoadingOverlay,
  TableViewport,
} from "@/shared/components/Table";
import { useErrorToast } from "@/shared/components/ErrorToast";

import { CursorResourceFilterBar } from "../../_components/CursorResourceFilterBar";
import { CursorResourcePagination } from "../../_components/CursorResourcePagination";
import type { CursorListState } from "../../_lib/cursor-list-state";
import {
  AddRoleModal,
  DeleteRoleModal,
  EditRoleModal,
  InfoRoleModal,
  RolePermissionsModal,
} from "./RoleActionModals";
import { setDefaultRoleAction } from "../_actions/update-role";
import { RolesTable } from "./RolesTable";

type RolesListContentProps = {
  canDeleteRoles: boolean;
  canManageRoles: boolean;
  canViewPermissions: boolean;
  meta: PaginationMeta;
  permissions: PermissionResponse[];
  roles: RoleResponse[];
  state: CursorListState;
};

type ActiveRoleModal =
  | {
      type: "add";
    }
  | {
      role: RoleResponse;
      type: "delete" | "edit" | "info" | "permissions";
    }
  | null;

export function RolesListContent({
  canDeleteRoles,
  canManageRoles,
  canViewPermissions,
  meta,
  permissions,
  roles,
  state,
}: RolesListContentProps) {
  const [activeModal, setActiveModal] = useState<ActiveRoleModal>(null);
  const [isTableLoading, setIsTableLoading] = useState(false);
  const nextCursorId = roles.at(-1)?.id;
  const hasNext = Boolean(nextCursorId) && meta.total > roles.length;
  const canAssignPermissions = canManageRoles && canViewPermissions;

  return (
    <>
      <CursorResourceFilterBar
        actions={
          canManageRoles ? (
            <button
              type="button"
              onClick={() => setActiveModal({ type: "add" })}
              className="inline-flex h-10 items-center justify-center gap-2 whitespace-nowrap rounded-md bg-[#0F2854] px-4 text-sm font-semibold text-white transition hover:bg-[#1C4D8D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] dark:bg-[#4988C4] dark:hover:bg-[#1C4D8D]"
            >
              <Image
                src={plusIcon}
                alt=""
                width={16}
                height={16}
                className="shrink-0"
              />
              Add Role
            </button>
          ) : null
        }
        filters={state}
        searchLabel="Search"
        searchPlaceholder="Search roles"
        onTableLoadingChange={setIsTableLoading}
      />

      <TableFrame>
        <TableViewport>
          <RolesTable
            roles={roles}
            renderDefault={(role) => (
              <RoleDefaultButton
                canManageRoles={canManageRoles}
                role={role}
              />
            )}
            renderActions={(role) => (
              <>
                <IconActionButton
                  icon={infoIcon}
                  label="Info"
                  onClick={() => setActiveModal({ type: "info", role })}
                />
                {canManageRoles ? (
                  <IconActionButton
                    icon={editIcon}
                    label="Edit"
                    onClick={() => setActiveModal({ type: "edit", role })}
                  />
                ) : null}
                {canAssignPermissions ? (
                  <IconActionButton
                    icon={permissionAssignIcon}
                    label="Permissions"
                    onClick={() =>
                      setActiveModal({ type: "permissions", role })
                    }
                  />
                ) : null}
                {canDeleteRoles ? (
                  <IconActionButton
                    icon={trashIcon}
                    label="Delete"
                    onClick={() => setActiveModal({ type: "delete", role })}
                    variant="danger"
                  />
                ) : null}
              </>
            )}
          />
          {isTableLoading ? <TableLoadingOverlay label="Loading roles" /> : null}
        </TableViewport>

        <CursorResourcePagination
          cursorId={state.cursorId}
          hasNext={hasNext}
          itemCount={roles.length}
          itemLabel="role"
          nextCursorId={nextCursorId}
          onTableLoadingChange={setIsTableLoading}
        />
      </TableFrame>

      {activeModal?.type === "add" ? (
        <AddRoleModal onClose={() => setActiveModal(null)} />
      ) : null}
      {activeModal?.type === "info" ? (
        <InfoRoleModal
          role={activeModal.role}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "edit" ? (
        <EditRoleModal
          role={activeModal.role}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "permissions" ? (
        <RolePermissionsModal
          allPermissions={permissions}
          role={activeModal.role}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "delete" ? (
        <DeleteRoleModal
          role={activeModal.role}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
    </>
  );
}

function RoleDefaultButton({
  canManageRoles,
  role,
}: {
  canManageRoles: boolean;
  role: RoleResponse;
}) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  if (role.is_default) {
    return (
      <button
        type="button"
        disabled
        className="inline-flex h-9 min-w-[8.5rem] cursor-not-allowed items-center justify-center rounded-md border border-[#4988C4]/40 bg-[#BDE8F5]/50 px-3 text-sm font-semibold text-[#0F2854] dark:text-[#BDE8F5]"
      >
        Default
      </button>
    );
  }

  return (
    <button
      type="button"
      disabled={!canManageRoles || pending}
      onClick={() => {
        startTransition(async () => {
          const result = await setDefaultRoleAction(role.id);

          if (!result.ok) {
            showError(result.error);
            return;
          }

          router.refresh();
        });
      }}
      className="group inline-flex h-9 min-w-[8.5rem] items-center justify-center rounded-md border border-[#D9EEF7] bg-white px-3 text-sm font-semibold text-[#0F2854] transition hover:border-[#4988C4] hover:bg-[#BDE8F5]/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] disabled:cursor-not-allowed disabled:opacity-60 dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-[#BDE8F5] dark:hover:bg-[#1C4D8D]/50"
    >
      <span className="relative inline-grid min-w-[7.25rem] grid-cols-1">
        <span className="col-start-1 row-start-1 transition-opacity group-hover:opacity-0 group-focus-visible:opacity-0">
          {pending ? "Saving" : "No"}
        </span>
        <span className="col-start-1 row-start-1 opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
          {pending ? "Saving" : "Set as Default"}
        </span>
      </span>
    </button>
  );
}
