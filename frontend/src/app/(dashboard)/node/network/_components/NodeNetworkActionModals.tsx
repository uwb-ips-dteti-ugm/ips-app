"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import type { NodeNetworkResponse } from "@/lib/api/node-network";
import {
  DescriptionList,
  DescriptionRow,
} from "@/shared/components/DescriptionList";
import { useErrorToast } from "@/shared/components/ErrorToast";
import { TextField } from "@/shared/components/FormControls";
import { Modal, ModalActions } from "@/shared/components/Modal";

import {
  createNodeNetworkAction,
  deleteNodeNetworkAction,
  updateNodeNetworkAction,
} from "../_actions/update-node-network";
import { formatPanId } from "./NodeNetworksTable";

type NodeNetworkModalProps = {
  nodeNetwork: NodeNetworkResponse;
  onClose: () => void;
};

export function AddNodeNetworkModal({ onClose }: { onClose: () => void }) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Add Node Network" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await createNodeNetworkAction({
              description: getFormString(formData, "description"),
              name: getFormString(formData, "name"),
              panId: getFormString(formData, "pan_id"),
            });

            if (!result.ok) {
              showError(result.error);
              return;
            }

            onClose();
            router.refresh();
          });
        }}
      >
        <TextField label="Name" name="name" required />
        <TextField
          label="PAN ID"
          name="pan_id"
          type="number"
          min={0}
          max={0xffff}
          step={1}
          inputMode="numeric"
          required
        />
        <TextField label="Description" name="description" />

        <ModalActions
          submitLabel="Add network"
          pendingLabel="Adding"
          pending={pending}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

export function EditNodeNetworkModal({
  nodeNetwork,
  onClose,
}: NodeNetworkModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Edit Node Network" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await updateNodeNetworkAction({
              description: getFormString(formData, "description"),
              name: getFormString(formData, "name"),
              nodeNetworkId: nodeNetwork.id,
              panId: getFormString(formData, "pan_id"),
            });

            if (!result.ok) {
              showError(result.error);
              return;
            }

            onClose();
            router.refresh();
          });
        }}
      >
        <TextField
          label="Name"
          name="name"
          defaultValue={nodeNetwork.name}
          required
        />
        <TextField
          label="PAN ID"
          name="pan_id"
          type="number"
          min={0}
          max={0xffff}
          step={1}
          inputMode="numeric"
          defaultValue={nodeNetwork.pan_id}
          required
        />
        <TextField
          label="Description"
          name="description"
          defaultValue={nodeNetwork.description}
        />

        <ModalActions
          submitLabel="Save"
          pendingLabel="Saving"
          pending={pending}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

export function InfoNodeNetworkModal({
  nodeNetwork,
  onClose,
}: NodeNetworkModalProps) {
  return (
    <Modal title="Node Network Info" onClose={onClose}>
      <DescriptionList>
        <DescriptionRow label="ID" value={nodeNetwork.id} />
        <DescriptionRow label="Name" value={nodeNetwork.name} />
        <DescriptionRow
          label="PAN ID"
          value={`${formatPanId(nodeNetwork.pan_id)} (${nodeNetwork.pan_id})`}
        />
        <DescriptionRow
          label="Description"
          value={nodeNetwork.description || "No description"}
        />
        <DescriptionRow
          label="Created"
          value={formatTimestamp(nodeNetwork.created_at)}
        />
        <DescriptionRow
          label="Updated"
          value={formatTimestamp(nodeNetwork.updated_at)}
        />
      </DescriptionList>
    </Modal>
  );
}

export function DeleteNodeNetworkModal({
  nodeNetwork,
  onClose,
}: NodeNetworkModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Delete Node Network" onClose={onClose} widthClassName="max-w-md">
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          startTransition(async () => {
            const result = await deleteNodeNetworkAction(nodeNetwork.id);
            if (!result.ok) {
              showError(result.error);
              return;
            }

            onClose();
            router.refresh();
          });
        }}
      >
        <p className="text-sm leading-6 text-[#0F2854] dark:text-white">
          Delete <span className="font-semibold">{nodeNetwork.name}</span>? This
          action cannot be undone.
        </p>

        <ModalActions
          submitLabel="Delete"
          pendingLabel="Deleting"
          pending={pending}
          onClose={onClose}
          destructive
        />
      </form>
    </Modal>
  );
}

function formatTimestamp(value: string | null): string {
  if (!value) {
    return "Not updated";
  }

  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(timestamp);
}

function getFormString(formData: FormData, name: string): string {
  return String(formData.get(name) ?? "").trim();
}
