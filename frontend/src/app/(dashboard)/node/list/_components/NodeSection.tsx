import { type NodeListItem, type NodeStatus } from "@/lib/api/nodes";
import { formatDate } from "@/lib/format";
import {
  DataTable,
  EmptyTableState,
  RowActions,
  TableBadge,
  TableCell,
  TableHead,
} from "@/shared/components/Table";

import {
  deleteNodeAction,
  restartNodeAction,
  setNodeStatusAction,
} from "../_actions/mutate-node";

type NodeSectionVariant = "waiting" | "approved";

type NodeSectionProps = {
  title: string;
  subtitle: string;
  emptyMessage: string;
  nodes: NodeListItem[];
  registeredNodeIds: Set<string>;
  canManage: boolean;
  canDelete: boolean;
  variant: NodeSectionVariant;
};

export function NodeSection({
  title,
  subtitle,
  emptyMessage,
  nodes,
  registeredNodeIds,
  canManage,
  canDelete,
  variant,
}: NodeSectionProps) {
  return (
    <section className="overflow-hidden rounded-md border border-[#D9EEF7] bg-white dark:border-[#1C4D8D] dark:bg-[#07111F]">
      <div className="border-b border-[#D9EEF7] px-4 py-3 dark:border-[#1C4D8D]">
        <h2 className="text-base font-semibold text-[#0F2854] dark:text-white">
          {title}
        </h2>
        <p className="mt-1 text-sm text-[#4988C4] dark:text-[#BDE8F5]">
          {subtitle}
        </p>
      </div>

      {nodes.length === 0 ? (
        <EmptyTableState message={emptyMessage} />
      ) : (
        <DataTable>
          <thead className="bg-[#EAF6FB] text-xs uppercase text-[#1C4D8D] dark:bg-[#0B1E38] dark:text-[#BDE8F5]">
            <tr>
              <TableHead>Name</TableHead>
              <TableHead>Device ID</TableHead>
              <TableHead>Connection</TableHead>
              <TableHead>Last Seen</TableHead>
              <TableHead>Actions</TableHead>
            </tr>
          </thead>
          <tbody>
            {nodes.map((node) => (
              <tr
                key={node.id}
                className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
              >
                <TableCell>
                  <div className="font-semibold text-[#0F2854] dark:text-white">
                    {node.name}
                  </div>
                  {node.description && (
                    <div className="mt-0.5 max-w-80 truncate text-xs text-[#4988C4] dark:text-[#BDE8F5]">
                      {node.description}
                    </div>
                  )}
                </TableCell>
                <TableCell>
                  <span className="font-mono text-xs">{node.device_id}</span>
                </TableCell>
                <TableCell className="text-center">
                  <ConnectionBadge
                    isConnected={registeredNodeIds.has(node.device_id)}
                  />
                </TableCell>
                <TableCell>{formatDate(node.last_seen_at)}</TableCell>
                <TableCell>
                  <NodeActions
                    node={node}
                    canManage={canManage}
                    canDelete={canDelete}
                    variant={variant}
                  />
                </TableCell>
              </tr>
            ))}
          </tbody>
        </DataTable>
      )}
    </section>
  );
}

function ConnectionBadge({ isConnected }: { isConnected: boolean }) {
  return (
    <TableBadge
      className={
        isConnected
          ? "border-[#4988C4]/40 bg-[#BDE8F5]/50 text-[#0F2854] dark:text-[#BDE8F5]"
          : "border-[#D9EEF7] bg-white text-[#4988C4] dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-[#BDE8F5]"
      }
    >
      {isConnected ? "connected" : "offline"}
    </TableBadge>
  );
}

function NodeActions({
  node,
  canManage,
  canDelete,
  variant,
}: {
  node: NodeListItem;
  canManage: boolean;
  canDelete: boolean;
  variant: NodeSectionVariant;
}) {
  return (
    <RowActions>
      {canManage && variant === "waiting" && (
        <StatusAction node={node} status="approved" label="Approve" />
      )}
      {canManage && variant === "approved" && (
        <>
          <RestartAction node={node} />
          <StatusAction node={node} status="suspended" label="Suspend" />
          <StatusAction node={node} status="revoked" label="Revoke" />
        </>
      )}
      {canDelete && <DeleteAction node={node} />}
    </RowActions>
  );
}

function StatusAction({
  node,
  status,
  label,
}: {
  node: NodeListItem;
  status: NodeStatus;
  label: string;
}) {
  return (
    <form action={setNodeStatusAction}>
      <input type="hidden" name="node_id" value={node.id} />
      <input type="hidden" name="status" value={status} />
      <NodeActionButton>{label}</NodeActionButton>
    </form>
  );
}

function RestartAction({ node }: { node: NodeListItem }) {
  return (
    <form action={restartNodeAction}>
      <input type="hidden" name="device_id" value={node.device_id} />
      <NodeActionButton>Restart</NodeActionButton>
    </form>
  );
}

function DeleteAction({ node }: { node: NodeListItem }) {
  return (
    <form action={deleteNodeAction}>
      <input type="hidden" name="node_id" value={node.id} />
      <NodeActionButton variant="danger">Delete</NodeActionButton>
    </form>
  );
}

function NodeActionButton({
  children,
  variant = "default",
}: {
  children: string;
  variant?: "default" | "danger";
}) {
  const className =
    variant === "danger"
      ? "h-8 rounded-md border border-[#E05A5A] px-2.5 text-xs font-semibold text-[#E05A5A] transition hover:bg-[#E05A5A] hover:text-white"
      : "h-8 rounded-md border border-[#4988C4] px-2.5 text-xs font-semibold text-[#1C4D8D] transition hover:bg-[#BDE8F5]/50 dark:text-[#BDE8F5] dark:hover:bg-[#1C4D8D]/50";

  return (
    <button type="submit" className={className}>
      {children}
    </button>
  );
}
