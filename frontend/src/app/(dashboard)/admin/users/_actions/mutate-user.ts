"use server";

import { revalidatePath } from "next/cache";

import {
  fetchBackend,
  getActionAccessToken,
  jsonBackend,
} from "@/lib/actions/backend";
import {
  type ActionState,
  getFormString,
  readErrorMessage,
} from "@/lib/actions/form";

export type UserMutationState = ActionState;

export async function registerUserAction(
  _state: UserMutationState,
  formData: FormData,
): Promise<UserMutationState> {
  const accessToken = await getActionAccessToken();

  const name = getFormString(formData, "name");
  const username = getFormString(formData, "username");
  const password = getFormString(formData, "password");
  const roleId = getFormString(formData, "role_id");

  if (!name || !username || !password || !roleId) {
    return {
      status: "error",
      message: "Name, username, password, and role are required.",
    };
  }

  const response = await jsonBackend(accessToken, "/auth/register", "POST", {
    name,
    username,
    password,
    role_id: roleId,
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to register user."),
    };
  }

  revalidatePath("/admin/users");
  return {
    status: "success",
    message: "User registered successfully.",
  };
}

export async function updateUserAction(
  _state: UserMutationState,
  formData: FormData,
): Promise<UserMutationState> {
  const accessToken = await getActionAccessToken();

  const userId = getFormString(formData, "user_id");
  const name = getFormString(formData, "name");
  const username = getFormString(formData, "username");
  const password = getFormString(formData, "password");
  const roleId = getFormString(formData, "role_id");
  const status = getFormString(formData, "status");

  if (!userId || !name || !status) {
    return {
      status: "error",
      message: "Name and status are required.",
    };
  }

  if (username) {
    const authInfoResponse = await patchBackend(
      accessToken,
      `/auth/${userId}/info`,
      {
        username,
      },
    );
    if (!authInfoResponse.ok) {
      return {
        status: "error",
        message: await readErrorMessage(
          authInfoResponse,
          "Failed to update username.",
        ),
      };
    }
  }

  if (password) {
    const passwordResponse = await patchBackend(
      accessToken,
      `/auth/${userId}/password`,
      {
        new_password: password,
      },
    );
    if (!passwordResponse.ok) {
      return {
        status: "error",
        message: await readErrorMessage(
          passwordResponse,
          "Failed to update password.",
        ),
      };
    }
  }

  const infoResponse = await patchBackend(
    accessToken,
    `/users/${userId}/info`,
    {
      name,
    },
  );
  if (!infoResponse.ok) {
    return {
      status: "error",
      message: await readErrorMessage(infoResponse, "Failed to update user info."),
    };
  }

  if (roleId) {
    const roleResponse = await patchBackend(
      accessToken,
      `/users/${userId}/role`,
      {
        role_id: roleId,
      },
    );
    if (!roleResponse.ok) {
      return {
        status: "error",
        message: await readErrorMessage(roleResponse, "Failed to update user role."),
      };
    }
  }

  const statusResponse = await patchBackend(
    accessToken,
    `/users/${userId}/status`,
    {
      status,
    },
  );
  if (!statusResponse.ok) {
    return {
      status: "error",
      message: await readErrorMessage(statusResponse, "Failed to update user status."),
    };
  }

  revalidatePath("/admin/users");
  return {
    status: "success",
    message: "User updated successfully.",
  };
}

export async function deleteUserAction(
  _state: UserMutationState,
  formData: FormData,
): Promise<UserMutationState> {
  const accessToken = await getActionAccessToken();

  const userId = getFormString(formData, "user_id");

  if (!userId) {
    return {
      status: "error",
      message: "User ID is required.",
    };
  }

  const response = await fetchBackend(accessToken, `/users/${userId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    return {
      status: "error",
      message: await readErrorMessage(response, "Failed to delete user."),
    };
  }

  revalidatePath("/admin/users");
  return {
    status: "success",
    message: "User deleted successfully.",
  };
}

async function patchBackend(
  accessToken: string,
  path: string,
  body: Record<string, string>,
): Promise<Response> {
  return jsonBackend(accessToken, path, "PATCH", body);
}
