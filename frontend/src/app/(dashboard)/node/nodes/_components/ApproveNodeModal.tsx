"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import type { NodeResponse } from "@/lib/api/node";
import { useErrorToast } from "@/shared/components/ErrorToast";
import { SelectField, TextField } from "@/shared/components/FormControls";
import { Modal, ModalActions } from "@/shared/components/Modal";

import { approveNodeAction } from "../_actions/approve-node";
import type { NodeNetworkFilterOption } from "../_lib/get-nodes-page-data";

type ApproveNodeModalProps = {
  networks: NodeNetworkFilterOption[];
  node: NodeResponse;
  onClose: () => void;
};

export function ApproveNodeModal({
  networks,
  node,
  onClose,
}: ApproveNodeModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Approve Node" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await approveNodeAction({
              address: getFormString(formData, "address"),
              name: getFormString(formData, "name"),
              networkId: getFormString(formData, "network_id"),
              nodeId: node.id,
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
        <p className="text-sm leading-6 text-[#0F2854] dark:text-white">
          Set the node name and assign a network address before approving{" "}
          <span className="font-semibold">{node.name}</span>.
        </p>

        <TextField label="Name" name="name" defaultValue={node.name} required />

        <SelectField
          label="Network"
          name="network_id"
          defaultValue={node.network?.id ?? networks[0]?.id ?? ""}
          disabled={networks.length === 0}
          required
        >
          {networks.length === 0 ? (
            <option value="">No node network available</option>
          ) : (
            networks.map((network) => (
              <option key={network.id} value={network.id}>
                {network.name} ({formatUwbValue(network.panId)})
              </option>
            ))
          )}
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
          required
        />

        <ModalActions
          submitLabel="Approve"
          pendingLabel="Approving"
          pending={pending}
          submitDisabled={networks.length === 0}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

function formatUwbValue(value: number): string {
  return `0x${value.toString(16).padStart(4, "0").toUpperCase()}`;
}

function getFormString(formData: FormData, name: string): string {
  return String(formData.get(name) ?? "").trim();
}
