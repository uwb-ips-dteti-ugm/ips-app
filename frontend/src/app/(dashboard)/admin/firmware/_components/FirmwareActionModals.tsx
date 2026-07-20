"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import type { FirmwareDeployResponse, FirmwareResponse } from "@/lib/api/firmware";
import { DescriptionList, DescriptionRow } from "@/shared/components/DescriptionList";
import { Modal, ModalActions } from "@/shared/components/Modal";
import { useErrorToast } from "@/shared/components/ErrorToast";

import { deleteFirmwareAction } from "../_actions/delete-firmware";
import { deployFirmwareAction } from "../_actions/deploy-firmware";

type FirmwareModalProps = {
  firmware: FirmwareResponse;
  onClose: () => void;
};

type DeployFirmwareModalProps = FirmwareModalProps & {
  connectedNodeCount: number;
};

export function DeployFirmwareModal({
  connectedNodeCount,
  firmware,
  onClose,
}: DeployFirmwareModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();
  const [result, setResult] = useState<FirmwareDeployResponse | null>(null);

  if (result) {
    return (
      <Modal title="Deployment Result" onClose={onClose} widthClassName="max-w-md">
        <div className="flex flex-col gap-4">
          <DescriptionList>
            <DescriptionRow label="Targeted nodes" value={String(result.targeted_count)} />
            <DescriptionRow label="Succeeded" value={String(result.succeeded_count)} />
            <DescriptionRow
              label="Failed"
              value={
                result.failed_device_ids.length === 0
                  ? "0"
                  : `${result.failed_device_ids.length} (${result.failed_device_ids.join(", ")})`
              }
            />
            <DescriptionRow
              label="Skipped (board variant mismatch)"
              value={String(result.skipped_count)}
            />
          </DescriptionList>
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => {
                onClose();
                router.refresh();
              }}
              className="inline-flex h-10 items-center justify-center rounded-md bg-[#0F2854] px-4 text-sm font-semibold text-white transition hover:bg-[#1C4D8D] dark:bg-[#4988C4] dark:hover:bg-[#1C4D8D]"
            >
              Close
            </button>
          </div>
        </div>
      </Modal>
    );
  }

  return (
    <Modal title="Deploy Firmware" onClose={onClose} widthClassName="max-w-md">
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          startTransition(async () => {
            const actionResult = await deployFirmwareAction(firmware.id);
            if (!actionResult.ok) {
              showError(actionResult.error);
              return;
            }

            setResult(actionResult.result);
          });
        }}
      >
        <p className="text-sm leading-6 text-[#0F2854] dark:text-white">
          Push firmware version <span className="font-semibold">{firmware.version}</span> (
          {firmware.board_variant}) to <span className="font-semibold">{connectedNodeCount}</span>{" "}
          currently connected node{connectedNodeCount === 1 ? "" : "s"}? Nodes will download and
          flash the update, then restart automatically.
        </p>

        {connectedNodeCount === 0 ? (
          <p className="text-sm font-semibold text-amber-600 dark:text-amber-400">
            No nodes are currently connected.
          </p>
        ) : null}

        <ModalActions
          submitLabel="Deploy"
          pendingLabel="Deploying"
          pending={pending}
          onClose={onClose}
          submitDisabled={connectedNodeCount === 0}
        />
      </form>
    </Modal>
  );
}

export function DeleteFirmwareModal({ firmware, onClose }: FirmwareModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Delete Firmware" onClose={onClose} widthClassName="max-w-md">
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          startTransition(async () => {
            const result = await deleteFirmwareAction(firmware.id);
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
          Delete firmware <span className="font-semibold">{firmware.version}</span> (
          {firmware.board_variant})? This action cannot be undone.
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
