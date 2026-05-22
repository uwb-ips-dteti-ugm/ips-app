"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, useTransition } from "react";

import type { PaginationMeta } from "@/lib/api/common";
import type { NodeResponse } from "@/lib/api/node";
import checkIcon from "@/shared/assets/CheckIcon.svg";
import editIcon from "@/shared/assets/EditIcon.svg";
import infoIcon from "@/shared/assets/InfoIcon.svg";
import {
  IconActionButton,
  TableFrame,
  TableLoadingOverlay,
  TableViewport,
} from "@/shared/components/Table";

import { CursorResourcePagination } from "../../../admin/_components/CursorResourcePagination";
import type { NodeNetworkFilterOption } from "../_lib/get-nodes-page-data";
import type { NodesListState } from "../_lib/nodes-list-state";
import { ApproveNodeModal } from "./ApproveNodeModal";
import { EditNodeModal } from "./EditNodeModal";
import { NodeInfoModal } from "./NodeInfoModal";
import { NodesFilterBar } from "./NodesFilterBar";
import { NodesTable } from "./NodesTable";

const NODES_AUTO_REFRESH_INTERVAL_MS = 3_000;

type NodesListContentProps = {
  canManageNodes: boolean;
  meta: PaginationMeta;
  networks: NodeNetworkFilterOption[];
  nodes: NodeResponse[];
  state: NodesListState;
};

type ActiveNodeModal =
  | {
      node: NodeResponse;
      type: "approve" | "edit" | "info";
    }
  | null;

export function NodesListContent({
  canManageNodes,
  meta,
  networks,
  nodes,
  state,
}: NodesListContentProps) {
  const router = useRouter();
  const [activeModal, setActiveModal] = useState<ActiveNodeModal>(null);
  const [isAutoRefreshPending, startAutoRefreshTransition] = useTransition();
  const [isTableLoading, setIsTableLoading] = useState(false);
  const nextCursorId = nodes.at(-1)?.id;
  const hasNext = Boolean(nextCursorId) && meta.total > nodes.length;

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      if (isAutoRefreshPending || isTableLoading) {
        return;
      }

      startAutoRefreshTransition(() => {
        router.refresh();
      });
    }, NODES_AUTO_REFRESH_INTERVAL_MS);

    return () => window.clearInterval(intervalId);
  }, [isAutoRefreshPending, isTableLoading, router]);

  return (
    <>
      <NodesFilterBar
        filters={state}
        networks={networks}
        onTableLoadingChange={setIsTableLoading}
      />

      <TableFrame>
        <TableViewport>
          <NodesTable
            nodes={nodes}
            renderActions={(node) => (
              <>
                <IconActionButton
                  icon={infoIcon}
                  label="Info"
                  onClick={() => setActiveModal({ node, type: "info" })}
                />
                {canManageNodes && node.status !== "pending" ? (
                  <IconActionButton
                    icon={editIcon}
                    label="Edit"
                    onClick={() => setActiveModal({ node, type: "edit" })}
                  />
                ) : null}
                {canManageNodes && node.status === "pending" ? (
                  <IconActionButton
                    icon={checkIcon}
                    label="Approve"
                    onClick={() => setActiveModal({ node, type: "approve" })}
                  />
                ) : null}
              </>
            )}
          />
          {isTableLoading ? <TableLoadingOverlay label="Loading nodes" /> : null}
        </TableViewport>

        <CursorResourcePagination
          cursorId={state.cursorId}
          hasNext={hasNext}
          itemCount={nodes.length}
          itemLabel="node"
          nextCursorId={nextCursorId}
          onTableLoadingChange={setIsTableLoading}
        />
      </TableFrame>

      {activeModal?.type === "info" ? (
        <NodeInfoModal
          node={activeModal.node}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "approve" ? (
        <ApproveNodeModal
          networks={networks}
          node={activeModal.node}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "edit" ? (
        <EditNodeModal
          networks={networks}
          node={activeModal.node}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
    </>
  );
}
