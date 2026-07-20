"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import type { UserResponse } from "@/lib/api/user";
import {
  DescriptionList,
  DescriptionRow,
} from "@/shared/components/DescriptionList";
import { useErrorToast } from "@/shared/components/ErrorToast";
import { SelectField, TextField } from "@/shared/components/FormControls";
import { Modal, ModalActions } from "@/shared/components/Modal";

import {
  deleteUserAction,
  registerUserAction,
  resetUserPasswordAction,
  updateUserInfoAction,
} from "../_actions/update-user";
import type { UserRoleFilterOption } from "../_lib/get-users-page-data";

type UserModalProps = {
  onClose: () => void;
  user: UserResponse;
};

export function InfoUserModal({ onClose, user }: UserModalProps) {
  return (
    <Modal title="User Info" onClose={onClose}>
      <DescriptionList>
        <DescriptionRow label="ID" value={user.id} />
        <DescriptionRow label="Name" value={user.name} />
        <DescriptionRow
          label="Username"
          value={user.username ?? "No username"}
        />
        <DescriptionRow label="Bio" value={user.bio || "No bio"} />
        <DescriptionRow label="Role" value={user.role.name} />
        <DescriptionRow label="Status" value={formatLabel(user.status)} />
        <DescriptionRow label="Created" value={formatTimestamp(user.created_at)} />
        <DescriptionRow label="Updated" value={formatTimestamp(user.updated_at)} />
      </DescriptionList>
    </Modal>
  );
}

export function AddUserModal({
  onClose,
  roles,
}: {
  onClose: () => void;
  roles: UserRoleFilterOption[];
}) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Add User" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await registerUserAction({
              name: getFormString(formData, "name"),
              password: getFormString(formData, "password"),
              roleId: getFormString(formData, "role_id"),
              username: getFormString(formData, "username"),
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
        <TextField label="Name" name="name" autoComplete="name" required />
        <TextField
          label="Username"
          name="username"
          autoComplete="username"
          required
        />
        <TextField
          label="Password"
          name="password"
          type="password"
          autoComplete="new-password"
          required
        />
        <SelectField
          label="Role"
          name="role_id"
          defaultValue={roles[0]?.id ?? ""}
          disabled={roles.length === 0}
          required
        >
          {roles.length === 0 ? (
            <option value="">No role available</option>
          ) : (
            roles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))
          )}
        </SelectField>

        <ModalActions
          submitLabel="Add user"
          pendingLabel="Adding"
          pending={pending}
          submitDisabled={roles.length === 0}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

export function EditUserModal({ onClose, user }: UserModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Edit User" onClose={onClose}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);

          startTransition(async () => {
            const result = await updateUserInfoAction({
              bio: getFormString(formData, "bio"),
              name: getFormString(formData, "name"),
              userId: user.id,
              username: getFormString(formData, "username"),
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
        <TextField label="Name" name="name" defaultValue={user.name} required />
        <TextField
          label="Username"
          name="username"
          defaultValue={user.username}
          required
        />
        <TextField label="Bio" name="bio" defaultValue={user.bio ?? ""} />

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

export function ResetUserPasswordModal({ onClose, user }: UserModalProps) {
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal
      title="Change Password"
      onClose={onClose}
      widthClassName="max-w-md"
    >
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);
          const newPassword = getFormString(formData, "new_password");
          const confirmPassword = getFormString(formData, "confirm_password");

          if (newPassword !== confirmPassword) {
            showError("Passwords do not match.");
            return;
          }

          startTransition(async () => {
            const result = await resetUserPasswordAction({
              newPassword,
              userId: user.id,
            });

            if (!result.ok) {
              showError(result.error);
              return;
            }

            onClose();
          });
        }}
      >
        <p className="text-sm leading-6 text-[#0F2854] dark:text-white">
          Set a new password for{" "}
          <span className="font-semibold">{user.name}</span>.
        </p>

        <TextField
          label="New password"
          name="new_password"
          type="password"
          autoComplete="new-password"
          required
        />
        <TextField
          label="Confirm password"
          name="confirm_password"
          type="password"
          autoComplete="new-password"
          required
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

export function DeleteUserModal({ onClose, user }: UserModalProps) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [pending, startTransition] = useTransition();

  return (
    <Modal title="Delete User" onClose={onClose} widthClassName="max-w-md">
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          startTransition(async () => {
            const result = await deleteUserAction(user.id);
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
          Delete <span className="font-semibold">{user.name}</span>? This action
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

function formatLabel(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function getFormString(formData: FormData, name: string): string {
  return String(formData.get(name) ?? "").trim();
}
