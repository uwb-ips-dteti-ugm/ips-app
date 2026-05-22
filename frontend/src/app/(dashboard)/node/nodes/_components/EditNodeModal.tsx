"use client";

import { useRouter } from "next/navigation";
import { useMemo, useTransition } from "react";

import type { NodeResponse } from "@/lib/api/node";
import { useErrorToast } from "@/shared/components/ErrorToast";
import { SelectField, TextField } from "@/shared/components/FormControls";
import { Modal, ModalActions } from "@/shared/components/Modal";

import { updateNodeAction } from "../_actions/update-node";
import type { NodeNetworkFilterOption } from "../_lib/get-nodes-page-data";

type EditNodeModalProps = {
  networks: NodeNetworkFilterOption[];
  node: NodeResponse;
  onClose: () => void;
};

export function EditNodeModal({
  networks,
  node,
  onClose,
}: EditNodeModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();
  const networkOptions = useMemo(
    () => mergeNetworkOptions(networks, node),
    [networks, node],
  );

  return (
    <Modal title="Edit Node" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await updateNodeAction({
              address: getFormString(formData, "address"),
              description: getFormString(formData, "description"),
              name: getFormString(formData, "name"),
              networkId: getFormString(formData, "network_id"),
              nodeId: node.id,
              status: getFormString(formData, "status"),
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
        <TextField label="Name" name="name" defaultValue={node.name} required />
        <TextField
          label="Description"
          name="description"
          defaultValue={node.description}
        />

        <SelectField
          label="Network"
          name="network_id"
          defaultValue={node.network?.id ?? ""}
        >
          <option value="">Unassigned</option>
          {networkOptions.map((network) => (
            <option key={network.id} value={network.id}>
              {network.name} ({formatUwbValue(network.panId)})
            </option>
          ))}
        </SelectField>

        <TextField
          label="Address"
          name="address"
          type="number"
          inputMode="numeric"
          min={0}
          max={0xffff}
          step={1}
          defaultValue={node.address ?? ""}
          placeholder="Unassigned"
        />

        <SelectField label="Status" name="status" defaultValue={node.status}>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="suspended">Suspended</option>
          <option value="revoked">Revoked</option>
        </SelectField>

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

function mergeNetworkOptions(
  networks: NodeNetworkFilterOption[],
  node: NodeResponse,
): NodeNetworkFilterOption[] {
  if (!node.network || networks.some((network) => network.id === node.network?.id)) {
    return networks;
  }

  return [
    {
      id: node.network.id,
      name: node.network.name,
      panId: node.network.pan_id,
    },
    ...networks,
  ];
}

function formatUwbValue(value: number): string {
  return `0x${value.toString(16).padStart(4, "0").toUpperCase()}`;
}

function getFormString(formData: FormData, name: string): string {
  return String(formData.get(name) ?? "").trim();
}
