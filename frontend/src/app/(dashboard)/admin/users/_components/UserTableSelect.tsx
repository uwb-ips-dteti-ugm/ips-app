"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState, useTransition, type ChangeEvent } from "react";

import type { UserResponse, UserStatus } from "@/lib/api/user";
import chevronDownIcon from "@/shared/assets/ChevronDownIcon.svg";
import { useErrorToast } from "@/shared/components/ErrorToast";

import {
  updateUserRoleAction,
  updateUserStatusAction,
  type UserUpdateActionResult,
} from "../_actions/update-user";
import type { UserRoleFilterOption } from "../_lib/get-users-page-data";

const USER_STATUS_OPTIONS: Array<{
  label: string;
  value: UserStatus;
}> = [
  { label: "Active", value: "active" },
  { label: "Suspended", value: "suspended" },
  { label: "Banned", value: "banned" },
];

type TableSelectProps<Value extends string> = {
  ariaLabel: string;
  options: Array<{
    label: string;
    value: Value;
  }>;
  onUpdate: (value: Value) => Promise<UserUpdateActionResult>;
  value: Value;
};

export function UserRoleSelect({
  roles,
  user,
}: {
  roles: UserRoleFilterOption[];
  user: UserResponse;
}) {
  return (
    <UserTableSelect
      ariaLabel={`Role for ${user.name}`}
      options={roles.map((role) => ({
        label: role.name,
        value: role.id,
      }))}
      value={user.role.id}
      onUpdate={(roleId) => updateUserRoleAction(user.id, roleId)}
    />
  );
}

export function UserStatusSelect({ user }: { user: UserResponse }) {
  return (
    <UserTableSelect
      ariaLabel={`Status for ${user.name}`}
      options={USER_STATUS_OPTIONS}
      value={user.status}
      onUpdate={(status) => updateUserStatusAction(user.id, status)}
    />
  );
}

function UserTableSelect<Value extends string>({
  ariaLabel,
  onUpdate,
  options,
  value: initialValue,
}: TableSelectProps<Value>) {
  const router = useRouter();
  const { showError } = useErrorToast();
  const [isPending, startTransition] = useTransition();
  const [value, setValue] = useState(initialValue);

  function updateValue(event: ChangeEvent<HTMLSelectElement>) {
    const nextValue = event.currentTarget.value as Value;
    const previousValue = value;

    if (nextValue === previousValue) {
      return;
    }

    setValue(nextValue);
    startTransition(async () => {
      try {
        const result = await onUpdate(nextValue);
        if (!result.ok) {
          setValue(previousValue);
          showError(result.error);
          return;
        }

        router.refresh();
      } catch {
        setValue(previousValue);
        showError("The user update could not be completed. Please try again.");
      }
    });
  }

  return (
    <div className="relative inline-block min-w-36 max-w-52">
      <select
        aria-label={ariaLabel}
        disabled={isPending || options.length === 0}
        value={value}
        onChange={updateValue}
        className="h-9 w-full appearance-none rounded-md border border-[#D9EEF7] bg-white py-0 pl-3 pr-9 text-sm font-medium text-[#0F2854] outline-none transition focus:border-[#4988C4] focus:ring-2 focus:ring-[#BDE8F5] disabled:cursor-wait disabled:opacity-65 dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-white"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <Image
        src={chevronDownIcon}
        alt=""
        width={16}
        height={16}
        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 dark:brightness-0 dark:invert"
      />
    </div>
  );
}
