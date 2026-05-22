"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import type { PermissionResponse } from "@/lib/api/permission";
import {
  DescriptionList,
  DescriptionRow,
} from "@/shared/components/DescriptionList";
import { useErrorToast } from "@/shared/components/ErrorToast";
import { TextField } from "@/shared/components/FormControls";
import { Modal, ModalActions } from "@/shared/components/Modal";

import {
  createPermissionAction,
  deletePermissionAction,
  updatePermissionAction,
} from "../_actions/update-permission";

type PermissionModalProps = {
  onClose: () => void;
  permission: PermissionResponse;
};

export function AddPermissionModal({ onClose }: { onClose: () => void }) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Add Permission" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await createPermissionAction({
              description: getFormString(formData, "description"),
              name: getFormString(formData, "name"),
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
        <TextField label="Description" name="description" />

        <ModalActions
          submitLabel="Add permission"
          pendingLabel="Adding"
          pending={pending}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

export function EditPermissionModal({
  onClose,
  permission,
}: PermissionModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Edit Permission" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await updatePermissionAction({
              description: getFormString(formData, "description"),
              name: getFormString(formData, "name"),
              permissionId: permission.id,
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
        <TextField label="Name" name="name" defaultValue={permission.name} required />
        <TextField
          label="Description"
          name="description"
          defaultValue={permission.description}
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

export function InfoPermissionModal({
  onClose,
  permission,
}: PermissionModalProps) {
  return (
    <Modal title="Permission Info" onClose={onClose}>
      <DescriptionList>
        <DescriptionRow label="ID" value={permission.id} />
        <DescriptionRow label="Name" value={permission.name} />
        <DescriptionRow
          label="Description"
          value={permission.description || "No description"}
        />
        <DescriptionRow
          label="Created"
          value={formatTimestamp(permission.created_at)}
        />
        <DescriptionRow
          label="Updated"
          value={formatTimestamp(permission.updated_at)}
        />
      </DescriptionList>
    </Modal>
  );
}

export function DeletePermissionModal({
  onClose,
  permission,
}: PermissionModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Delete Permission" onClose={onClose} widthClassName="max-w-md">
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          startTransition(async () => {
            const result = await deletePermissionAction(permission.id);
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
          Delete <span className="font-semibold">{permission.name}</span>? This
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
