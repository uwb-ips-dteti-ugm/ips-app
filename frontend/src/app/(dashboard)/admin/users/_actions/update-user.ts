"use server";

import { revalidatePath } from "next/cache";

import { register, resetUserPassword } from "@/lib/api/auth";
import { isApiError } from "@/lib/api/client";
import {
  deleteUser,
  updateUserInfo,
  updateUserRole,
  updateUserStatus,
  type UserStatus,
} from "@/lib/api/user";
import { getAuthSession } from "@/lib/auth/session";

const USERS_PATH = "/admin/users";

export type UserUpdateActionResult =
  | {
      ok: true;
    }
  | {
      error: string;
      ok: false;
    };

export async function registerUserAction({
  name,
  password,
  roleId,
  username,
}: {
  name: string;
  password: string;
  roleId: string;
  username: string;
}): Promise<UserUpdateActionResult> {
  if (!name || !username || !password || !roleId) {
    return {
      error: "Name, username, password, and role are required.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before adding users.",
      ok: false,
    };
  }

  try {
    await register(
      {
        name,
        password,
        role_id: roleId,
        username,
      },
      { accessToken: session.accessToken },
    );
    revalidatePath(USERS_PATH);
    return { ok: true };
  } catch (error) {
    return updateErrorResult(error, "The user could not be added.");
  }
}

export async function updateUserInfoAction({
  bio,
  name,
  userId,
  username,
}: {
  bio: string;
  name: string;
  userId: string;
  username: string;
}): Promise<UserUpdateActionResult> {
  if (!userId || !name || !username) {
    return {
      error: "Name and username are required.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before updating users.",
      ok: false,
    };
  }

  try {
    await updateUserInfo(
      userId,
      { bio, name, username },
      { accessToken: session.accessToken },
    );
    revalidatePath(USERS_PATH);
    return { ok: true };
  } catch (error) {
    return updateErrorResult(error, "The user could not be updated.");
  }
}

export async function resetUserPasswordAction({
  newPassword,
  userId,
}: {
  newPassword: string;
  userId: string;
}): Promise<UserUpdateActionResult> {
  if (!userId || !newPassword) {
    return {
      error: "Enter a new password before saving.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before updating users.",
      ok: false,
    };
  }

  try {
    await resetUserPassword(
      userId,
      { new_password: newPassword },
      { accessToken: session.accessToken },
    );
    return { ok: true };
  } catch (error) {
    return updateErrorResult(error, "The user password could not be reset.");
  }
}

export async function updateUserRoleAction(
  userId: string,
  roleId: string,
): Promise<UserUpdateActionResult> {
  if (!userId || !roleId) {
    return {
      error: "Select a role before updating this user.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before updating users.",
      ok: false,
    };
  }

  try {
    await updateUserRole(
      userId,
      { role_id: roleId },
      { accessToken: session.accessToken },
    );
    revalidatePath(USERS_PATH);
    return { ok: true };
  } catch (error) {
    return updateErrorResult(error, "The user role could not be updated.");
  }
}

export async function updateUserStatusAction(
  userId: string,
  status: UserStatus,
): Promise<UserUpdateActionResult> {
  if (!userId || !isUserStatus(status)) {
    return {
      error: "Select a valid status before updating this user.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before updating users.",
      ok: false,
    };
  }

  try {
    await updateUserStatus(
      userId,
      { status },
      { accessToken: session.accessToken },
    );
    revalidatePath(USERS_PATH);
    return { ok: true };
  } catch (error) {
    return updateErrorResult(error, "The user status could not be updated.");
  }
}

export async function deleteUserAction(
  userId: string,
): Promise<UserUpdateActionResult> {
  if (!userId) {
    return {
      error: "Select a user before deleting.",
      ok: false,
    };
  }

  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before deleting users.",
      ok: false,
    };
  }

  try {
    await deleteUser(userId, { accessToken: session.accessToken });
    revalidatePath(USERS_PATH);
    return { ok: true };
  } catch (error) {
    return updateErrorResult(error, "The user could not be deleted.");
  }
}

function isUserStatus(value: string): value is UserStatus {
  return ["active", "suspended", "banned"].includes(value);
}

function updateErrorResult(
  error: unknown,
  fallback: string,
): UserUpdateActionResult {
  return {
    error: isApiError(error) ? error.message : fallback,
    ok: false,
  };
}
