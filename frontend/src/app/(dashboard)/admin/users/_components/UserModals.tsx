"use client";

import { useRouter } from "next/navigation";
import { useActionState, useEffect } from "react";

import { initialActionState } from "@/lib/actions/form";
import { formatDate, formatLabel } from "@/lib/format";
import {
  DescriptionList,
  DescriptionRow,
} from "@/shared/components/DescriptionList";
import {
  ActionMessage,
  SelectField,
  TextField,
} from "@/shared/components/FormControls";
import { Modal, ModalActions } from "@/shared/components/Modal";

import {
  deleteUserAction,
  registerUserAction,
  updateUserAction,
  type UserMutationState,
} from "../_actions/mutate-user";
import { type UserRoleFilterOption } from "./UsersSearchForm";
import { type UserListItem, type UserStatus } from "./UsersTable";

const userStatusOptions: Array<{ value: UserStatus; label: string }> = [
  { value: "active", label: "Active" },
  { value: "suspended", label: "Suspended" },
  { value: "banned", label: "Banned" },
];

type UserModalProps = {
  roles: UserRoleFilterOption[];
  onClose: () => void;
};

type EditUserModalProps = UserModalProps & {
  user: UserListItem;
};

type UserOnlyModalProps = {
  user: UserListItem;
  onClose: () => void;
};

export function RegisterUserModal({ roles, onClose }: UserModalProps) {
  const [state, formAction, pending] = useActionState(
    registerUserAction,
    initialActionState,
  );
  useCloseOnSuccess(state, onClose);

  return (
    <Modal title="Register User" onClose={onClose}>
      <form action={formAction} className="flex flex-col gap-4">
        <div className="flex flex-col gap-4">
          <TextField
            label="Name"
            name="name"
            autoComplete="name"
            required
          />
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
        </div>

        <ActionMessage state={state} />

        <ModalActions
          submitLabel="Register"
          pendingLabel="Registering"
          pending={pending}
          submitDisabled={roles.length === 0}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

export function EditUserModal({ user, roles, onClose }: EditUserModalProps) {
  const [state, formAction, pending] = useActionState(
    updateUserAction,
    initialActionState,
  );
  useCloseOnSuccess(state, onClose);

  return (
    <Modal title="Edit User" onClose={onClose}>
      <form action={formAction} className="flex flex-col gap-4">
        <input name="user_id" type="hidden" value={user.id} />

        <div className="flex flex-col gap-4">
          <TextField
            label="Name"
            name="name"
            defaultValue={user.name}
            autoComplete="name"
            required
          />
          <TextField
            label="Username"
            name="username"
            defaultValue={user.username ?? ""}
            autoComplete="username"
          />
          <TextField
            label="Password"
            name="password"
            type="password"
            autoComplete="new-password"
          />
          <SelectField
            label="Role"
            name="role_id"
            defaultValue={user.role?.id ?? ""}
            disabled={roles.length === 0}
          >
            {user.role ? null : <option value="">No role</option>}
            {roles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="Status"
            name="status"
            defaultValue={user.status}
            required
          >
            {userStatusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </SelectField>
        </div>

        <ActionMessage state={state} />

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

export function InfoUserModal({ user, onClose }: UserOnlyModalProps) {
  return (
    <Modal title="User Info" onClose={onClose}>
      <DescriptionList>
        <DescriptionRow label="Name" value={user.name} />
        <DescriptionRow label="Username" value={user.username ?? "No username"} />
        <DescriptionRow label="Bio" value={user.bio || "No bio"} />
        <DescriptionRow label="Role" value={user.role?.name ?? "No role"} />
        <DescriptionRow label="State" value={formatLabel(user.state)} />
        <DescriptionRow label="Status" value={formatLabel(user.status)} />
        <DescriptionRow
          label="Last Activity"
          value={formatDate(user.last_activity_at)}
        />
        <DescriptionRow
          label="Last Signed In"
          value={formatDate(user.last_signed_in_at)}
        />
        <DescriptionRow
          label="Last Refreshed"
          value={formatDate(user.last_refreshed_at)}
        />
        <DescriptionRow label="Created" value={formatDate(user.created_at)} />
        <DescriptionRow label="Updated" value={formatDate(user.updated_at)} />
        <DescriptionRow label="Version" value={String(user.version)} />
      </DescriptionList>
    </Modal>
  );
}

export function DeleteUserModal({ user, onClose }: UserOnlyModalProps) {
  const [state, formAction, pending] = useActionState(
    deleteUserAction,
    initialActionState,
  );
  useCloseOnSuccess(state, onClose);

  return (
    <Modal title="Delete User" onClose={onClose} widthClassName="max-w-md">
      <form action={formAction} className="flex flex-col gap-4">
        <input name="user_id" type="hidden" value={user.id} />
        <p className="text-sm leading-6 text-[#0F2854] dark:text-white">
          Delete <span className="font-semibold">{user.name}</span>? This action
          cannot be undone.
        </p>

        <ActionMessage state={state} />

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

function useCloseOnSuccess(state: UserMutationState, onClose: () => void) {
  const router = useRouter();

  useEffect(() => {
    if (state.status !== "success") {
      return;
    }

    onClose();
    router.refresh();
  }, [onClose, router, state.status]);
}
