"use client";

import Image from "next/image";
import { useState } from "react";

import type { PaginationMeta } from "@/lib/api/common";
import type { NodeNetworkResponse } from "@/lib/api/node-network";
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

import { CursorResourceFilterBar } from "../../../admin/_components/CursorResourceFilterBar";
import { CursorResourcePagination } from "../../../admin/_components/CursorResourcePagination";
import type { CursorListState } from "../../../admin/_lib/cursor-list-state";
import {
  AddNodeNetworkModal,
  DeleteNodeNetworkModal,
  EditNodeNetworkModal,
  InfoNodeNetworkModal,
} from "./NodeNetworkActionModals";
import { NodeNetworksTable } from "./NodeNetworksTable";

type NodeNetworksListContentProps = {
  canDeleteNodeNetworks: boolean;
  canManageNodeNetworks: boolean;
  meta: PaginationMeta;
  nodeNetworks: NodeNetworkResponse[];
  state: CursorListState;
};

type ActiveNodeNetworkModal =
  | {
      type: "add";
    }
  | {
      nodeNetwork: NodeNetworkResponse;
      type: "delete" | "edit" | "info";
    }
  | null;

export function NodeNetworksListContent({
  canDeleteNodeNetworks,
  canManageNodeNetworks,
  meta,
  nodeNetworks,
  state,
}: NodeNetworksListContentProps) {
  const [activeModal, setActiveModal] = useState<ActiveNodeNetworkModal>(null);
  const [isTableLoading, setIsTableLoading] = useState(false);
  const nextCursorId = nodeNetworks.at(-1)?.id;
  const hasNext = Boolean(nextCursorId) && meta.total > nodeNetworks.length;

  return (
    <>
      <CursorResourceFilterBar
        actions={
          canManageNodeNetworks ? (
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
              Add Network
            </button>
          ) : null
        }
        filters={state}
        searchLabel="Search"
        searchPlaceholder="Search node networks"
        onTableLoadingChange={setIsTableLoading}
      />

      <TableFrame>
        <TableViewport>
          <NodeNetworksTable
            nodeNetworks={nodeNetworks}
            renderActions={(nodeNetwork) => (
              <>
                <IconActionButton
                  icon={infoIcon}
                  label="Info"
                  onClick={() => setActiveModal({ type: "info", nodeNetwork })}
                />
                {canManageNodeNetworks ? (
                  <IconActionButton
                    icon={editIcon}
                    label="Edit"
                    onClick={() => setActiveModal({ type: "edit", nodeNetwork })}
                  />
                ) : null}
                {canDeleteNodeNetworks ? (
                  <IconActionButton
                    icon={trashIcon}
                    label="Delete"
                    onClick={() =>
                      setActiveModal({ type: "delete", nodeNetwork })
                    }
                    variant="danger"
                  />
                ) : null}
              </>
            )}
          />
          {isTableLoading ? (
            <TableLoadingOverlay label="Loading node networks" />
          ) : null}
        </TableViewport>

        <CursorResourcePagination
          cursorId={state.cursorId}
          hasNext={hasNext}
          itemCount={nodeNetworks.length}
          itemLabel="node network"
          nextCursorId={nextCursorId}
          onTableLoadingChange={setIsTableLoading}
        />
      </TableFrame>

      {activeModal?.type === "add" ? (
        <AddNodeNetworkModal onClose={() => setActiveModal(null)} />
      ) : null}
      {activeModal?.type === "info" ? (
        <InfoNodeNetworkModal
          nodeNetwork={activeModal.nodeNetwork}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "edit" ? (
        <EditNodeNetworkModal
          nodeNetwork={activeModal.nodeNetwork}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "delete" ? (
        <DeleteNodeNetworkModal
          nodeNetwork={activeModal.nodeNetwork}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
    </>
  );
}
