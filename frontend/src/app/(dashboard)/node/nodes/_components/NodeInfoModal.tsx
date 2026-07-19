"use client";

import type { NodeResponse } from "@/lib/api/node";
import {
  DescriptionList,
  DescriptionRow,
} from "@/shared/components/DescriptionList";
import { Modal } from "@/shared/components/Modal";

import { formatAddress, formatTimestamp } from "./NodesTable";

type NodeInfoModalProps = {
  node: NodeResponse;
  onClose: () => void;
};

export function NodeInfoModal({ node, onClose }: NodeInfoModalProps) {
  return (
    <Modal title="Node Info" onClose={onClose}>
      <DescriptionList>
        <DescriptionRow label="ID" value={node.id} />
        <DescriptionRow label="Device ID" value={node.device_id} />
        <DescriptionRow label="Name" value={node.name} />
        <DescriptionRow
          label="Description"
          value={node.description || "No description"}
        />
        <DescriptionRow
          label="Network"
          value={
            node.network
              ? `${node.network.name} (PAN ${node.network.pan_id})`
              : "Unassigned"
          }
        />
        <DescriptionRow label="Address" value={formatAddress(node.address)} />
        <DescriptionRow label="Status" value={formatLabel(node.status)} />
        <DescriptionRow
          label="Approved"
          value={node.status === "approved" ? "Yes" : "No"}
        />
        <DescriptionRow
          label="Approved At"
          value={formatTimestamp(node.approved_at, "Not approved")}
        />
        <DescriptionRow
          label="Approved By"
          value={node.approved_by ?? "Not approved"}
        />
        <DescriptionRow
          label="Last Seen"
          value={formatTimestamp(node.last_seen_at, "Never")}
        />
        <DescriptionRow
          label="Last Connected"
          value={formatTimestamp(node.last_connected_at, "Never")}
        />
        <DescriptionRow
          label="Last Disconnected"
          value={formatTimestamp(node.last_disconnected_at, "Never")}
        />
        <DescriptionRow
          label="Created"
          value={formatTimestamp(node.created_at, "Unknown")}
        />
        <DescriptionRow
          label="Updated"
          value={formatTimestamp(node.updated_at, "Not updated")}
        />
      </DescriptionList>
    </Modal>
  );
}

function formatLabel(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
