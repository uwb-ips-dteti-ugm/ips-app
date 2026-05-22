"use client";

import Image from "next/image";
import { useState } from "react";

import type { PaginationMeta } from "@/lib/api/common";
import type { PermissionResponse } from "@/lib/api/permission";
import editIcon from "@/shared/assets/EditIcon.svg";
import infoIcon from "@/shared/assets/InfoIcon.svg";
import plusIcon from "@/shared/assets/PlusIcon.svg";
import trashIcon from "@/shared/assets/TrashIcon.svg";
import {
  IconActionButton,
  TableFrame,
  TableLoadingOverlay,
  TableViewport,
} from "@/shared/components/Table";

import { CursorResourceFilterBar } from "../../_components/CursorResourceFilterBar";
import { CursorResourcePagination } from "../../_components/CursorResourcePagination";
import type { CursorListState } from "../../_lib/cursor-list-state";
import {
  AddPermissionModal,
  DeletePermissionModal,
  EditPermissionModal,
  InfoPermissionModal,
} from "./PermissionActionModals";
import { PermissionsTable } from "./PermissionsTable";

type PermissionsListContentProps = {
  canDeletePermissions: boolean;
  canManagePermissions: boolean;
  meta: PaginationMeta;
  permissions: PermissionResponse[];
  state: CursorListState;
};

type ActivePermissionModal =
  | {
      type: "add";
    }
  | {
      permission: PermissionResponse;
      type: "delete" | "edit" | "info";
    }
  | null;

export function PermissionsListContent({
  canDeletePermissions,
  canManagePermissions,
  meta,
  permissions,
  state,
}: PermissionsListContentProps) {
  const [activeModal, setActiveModal] = useState<ActivePermissionModal>(null);
  const [isTableLoading, setIsTableLoading] = useState(false);
  const nextCursorId = permissions.at(-1)?.id;
  const hasNext = Boolean(nextCursorId) && meta.total > permissions.length;

  return (
    <>
      <CursorResourceFilterBar
        actions={
          canManagePermissions ? (
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
              Add Permission
            </button>
          ) : null
        }
        filters={state}
        searchLabel="Search"
        searchPlaceholder="Search permissions"
        onTableLoadingChange={setIsTableLoading}
      />

      <TableFrame>
        <TableViewport>
          <PermissionsTable
            permissions={permissions}
            renderActions={(permission) => (
              <>
                <IconActionButton
                  icon={infoIcon}
                  label="Info"
                  onClick={() => setActiveModal({ type: "info", permission })}
                />
                {canManagePermissions ? (
                  <IconActionButton
                    icon={editIcon}
                    label="Edit"
                    onClick={() => setActiveModal({ type: "edit", permission })}
                  />
                ) : null}
                {canDeletePermissions ? (
                  <IconActionButton
                    icon={trashIcon}
                    label="Delete"
                    onClick={() =>
                      setActiveModal({ type: "delete", permission })
                    }
                    variant="danger"
                  />
                ) : null}
              </>
            )}
          />
          {isTableLoading ? (
            <TableLoadingOverlay label="Loading permissions" />
          ) : null}
        </TableViewport>

        <CursorResourcePagination
          cursorId={state.cursorId}
          hasNext={hasNext}
          itemCount={permissions.length}
          itemLabel="permission"
          nextCursorId={nextCursorId}
          onTableLoadingChange={setIsTableLoading}
        />
      </TableFrame>

      {activeModal?.type === "add" ? (
        <AddPermissionModal onClose={() => setActiveModal(null)} />
      ) : null}
      {activeModal?.type === "info" ? (
        <InfoPermissionModal
          permission={activeModal.permission}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "edit" ? (
        <EditPermissionModal
          permission={activeModal.permission}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "delete" ? (
        <DeletePermissionModal
          permission={activeModal.permission}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
    </>
  );
}
