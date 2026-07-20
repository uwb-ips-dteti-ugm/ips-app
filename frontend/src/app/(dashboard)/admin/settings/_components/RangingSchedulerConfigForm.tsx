"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import type { RangingSchedulerConfigResponse } from "@/lib/api/ranging-scheduler-config";
import { useErrorToast } from "@/shared/components/ErrorToast";
import { TextField } from "@/shared/components/FormControls";
import { Modal, ModalActions } from "@/shared/components/Modal";

import {
  resetRangingSchedulerConfigAction,
  updateRangingSchedulerConfigAction,
} from "../_actions/update-ranging-scheduler-config";

type RangingSchedulerConfigFormProps = {
  canManage: boolean;
  config: RangingSchedulerConfigResponse;
};

export function RangingSchedulerConfigForm({
  canManage,
  config,
}: RangingSchedulerConfigFormProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();
  const [isResetModalOpen, setIsResetModalOpen] = useState(false);

  return (
    <>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await updateRangingSchedulerConfigAction({
              idle_delay_ms: getFormNumber(formData, "idle_delay_ms"),
              initiate_timeout_uus: getFormNumber(
                formData,
                "initiate_timeout_uus",
              ),
              listen_timeout_uus: getFormNumber(formData, "listen_timeout_uus"),
              listen_to_initiate_delay_ms: getFormNumber(
                formData,
                "listen_to_initiate_delay_ms",
              ),
              pair_delay_ms: getFormNumber(formData, "pair_delay_ms"),
            });

            if (!result.ok) {
              showError(result.error);
              return;
            }

            router.refresh();
          });
        }}
      >
        <TextField
          label="Listen Timeout (µs)"
          name="listen_timeout_uus"
          type="number"
          min={1}
          defaultValue={config.listen_timeout_uus}
          disabled={!canManage}
          required
        />
        <TextField
          label="Initiate Timeout (µs)"
          name="initiate_timeout_uus"
          type="number"
          min={1}
          defaultValue={config.initiate_timeout_uus}
          disabled={!canManage}
          required
        />
        <TextField
          label="Listen-to-Initiate Delay (ms)"
          name="listen_to_initiate_delay_ms"
          type="number"
          min={1}
          defaultValue={config.listen_to_initiate_delay_ms}
          disabled={!canManage}
          required
        />
        <TextField
          label="Pair Delay (ms)"
          name="pair_delay_ms"
          type="number"
          min={1}
          defaultValue={config.pair_delay_ms}
          disabled={!canManage}
          required
        />
        <TextField
          label="Idle Delay (ms)"
          name="idle_delay_ms"
          type="number"
          min={1}
          defaultValue={config.idle_delay_ms}
          disabled={!canManage}
          required
        />

        {canManage ? (
          <div className="flex flex-wrap justify-end gap-2 border-t border-[#D9EEF7] pt-4 dark:border-[#1C4D8D]">
            <button
              type="button"
              disabled={pending}
              onClick={() => setIsResetModalOpen(true)}
              className="inline-flex h-10 items-center justify-center rounded-md border border-[#D9EEF7] bg-white px-4 text-sm font-semibold text-[#0F2854] transition hover:bg-[#BDE8F5]/35 disabled:cursor-not-allowed disabled:opacity-60 dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-[#BDE8F5] dark:hover:bg-[#1C4D8D]/40"
            >
              Reset to default
            </button>
            <button
              type="submit"
              disabled={pending}
              className="inline-flex h-10 items-center justify-center rounded-md bg-[#0F2854] px-4 text-sm font-semibold text-white transition hover:bg-[#1C4D8D] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#4988C4] dark:hover:bg-[#1C4D8D]"
            >
              {pending ? "Saving" : "Save"}
            </button>
          </div>
        ) : null}
      </form>

      {isResetModalOpen ? (
        <ResetRangingSchedulerConfigModal
          onClose={() => setIsResetModalOpen(false)}
        />
      ) : null}
    </>
  );
}

function ResetRangingSchedulerConfigModal({
  onClose,
}: {
  onClose: () => void;
}) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal
      title="Reset Ranging Scheduler Settings"
      onClose={onClose}
      widthClassName="max-w-md"
    >
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          startTransition(async () => {
            const result = await resetRangingSchedulerConfigAction();
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
          Reset all ranging scheduler parameters to their default values? This
          action cannot be undone.
        </p>

        <ModalActions
          submitLabel="Reset"
          pendingLabel="Resetting"
          pending={pending}
          onClose={onClose}
          destructive
        />
      </form>
    </Modal>
  );
}

function getFormNumber(formData: FormData, name: string): number {
  return Number(formData.get(name));
}
