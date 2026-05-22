"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import type { PermissionResponse } from "@/lib/api/permission";
import type { RoleResponse } from "@/lib/api/role";
import {
  DescriptionList,
  DescriptionRow,
} from "@/shared/components/DescriptionList";
import { useErrorToast } from "@/shared/components/ErrorToast";
import { TextField } from "@/shared/components/FormControls";
import { Modal, ModalActions } from "@/shared/components/Modal";

import {
  createRoleAction,
  deleteRoleAction,
  updateRoleAction,
  updateRolePermissionsAction,
} from "../_actions/update-role";

type RoleModalProps = {
  onClose: () => void;
  role: RoleResponse;
};

export function AddRoleModal({ onClose }: { onClose: () => void }) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Add Role" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await createRoleAction({
              description: getFormString(formData, "description"),
              isDefault: formData.get("is_default") === "on",
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
        <CheckboxField label="Set as default role" name="is_default" />

        <ModalActions
          submitLabel="Add role"
          pendingLabel="Adding"
          pending={pending}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

export function EditRoleModal({ onClose, role }: RoleModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Edit Role" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await updateRoleAction({
              description: getFormString(formData, "description"),
              makeDefault: formData.get("make_default") === "on",
              name: getFormString(formData, "name"),
              roleId: role.id,
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
        <TextField label="Name" name="name" defaultValue={role.name} required />
        <TextField
          label="Description"
          name="description"
          defaultValue={role.description}
        />
        {!role.is_default ? (
          <CheckboxField label="Set as default role" name="make_default" />
        ) : null}

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

export function RolePermissionsModal({
  allPermissions,
  onClose,
  role,
}: RoleModalProps & {
  allPermissions: PermissionResponse[];
}) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();
  const currentPermissionIds = role.permissions.map((permission) => permission.id);

  return (
    <Modal title="Role Permissions" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);
          const nextPermissionIds = formData
            .getAll("permission_ids")
            .map((value) => String(value));

          startTransition(async () => {
            const result = await updateRolePermissionsAction({
              currentPermissionIds,
              nextPermissionIds,
              roleId: role.id,
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
          Select permissions for <span className="font-semibold">{role.name}</span>.
        </p>
        <div className="max-h-72 overflow-y-auto rounded-md border border-[#D9EEF7] dark:border-[#1C4D8D]">
          {allPermissions.length === 0 ? (
            <div className="px-3 py-4 text-sm text-[#4988C4] dark:text-[#BDE8F5]">
              No permissions available.
            </div>
          ) : (
            allPermissions.map((permission) => (
              <label
                key={permission.id}
                className="flex cursor-pointer items-start gap-3 border-b border-[#D9EEF7] px-3 py-3 last:border-b-0 dark:border-[#1C4D8D]"
              >
                <input
                  type="checkbox"
                  name="permission_ids"
                  value={permission.id}
                  defaultChecked={currentPermissionIds.includes(permission.id)}
                  className="mt-1 h-4 w-4 accent-[#0F2854] dark:accent-[#4988C4]"
                />
                <span>
                  <span className="block text-sm font-semibold text-[#0F2854] dark:text-white">
                    {permission.name}
                  </span>
                  <span className="block text-xs leading-5 text-[#4988C4] dark:text-[#BDE8F5]">
                    {permission.description || "No description"}
                  </span>
                </span>
              </label>
            ))
          )}
        </div>

        <ModalActions
          submitLabel="Save permissions"
          pendingLabel="Saving"
          pending={pending}
          submitDisabled={allPermissions.length === 0}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

export function InfoRoleModal({ onClose, role }: RoleModalProps) {
  return (
    <Modal title="Role Info" onClose={onClose}>
      <DescriptionList>
        <DescriptionRow label="ID" value={role.id} />
        <DescriptionRow label="Name" value={role.name} />
        <DescriptionRow
          label="Description"
          value={role.description || "No description"}
        />
        <DescriptionRow label="Default" value={role.is_default ? "Yes" : "No"} />
        <DescriptionRow
          label="Permissions"
          value={
            role.permissions.length > 0
              ? role.permissions.map((permission) => permission.name).join(", ")
              : "No permissions"
          }
        />
        <DescriptionRow label="Created" value={formatTimestamp(role.created_at)} />
        <DescriptionRow label="Updated" value={formatTimestamp(role.updated_at)} />
      </DescriptionList>
    </Modal>
  );
}

export function DeleteRoleModal({ onClose, role }: RoleModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Delete Role" onClose={onClose} widthClassName="max-w-md">
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          startTransition(async () => {
            const result = await deleteRoleAction(role.id);
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
          Delete <span className="font-semibold">{role.name}</span>? This action
          cannot be undone.
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

function CheckboxField({ label, name }: { label: string; name: string }) {
  return (
    <label className="flex items-center gap-2 text-sm font-medium text-[#0F2854] dark:text-white">
      <input
        type="checkbox"
        name={name}
        className="h-4 w-4 accent-[#0F2854] dark:accent-[#4988C4]"
      />
      {label}
    </label>
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
