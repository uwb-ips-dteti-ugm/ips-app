"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { apiBaseUrl, getAuthHeaders } from "@/lib/api/client";
import {
  type ActionState,
  getFormString,
  readErrorMessage,
} from "@/lib/actions/form";
import { getAuthSession } from "@/lib/auth/session";

export type UserMutationState = ActionState;

export async function registerUserAction(
  _state: UserMutationState,
  formData: FormData,
): Promise<UserMutationState> {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

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

  const response = await fetch(new URL("/auth/register", apiBaseUrl), {
    method: "POST",
    headers: {
      ...getAuthHeaders(session.accessToken),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name,
      username,
      password,
      role_id: roleId,
    }),
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

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
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

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
      session.accessToken,
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
      session.accessToken,
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
    session.accessToken,
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
      session.accessToken,
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
    session.accessToken,
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
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const userId = getFormString(formData, "user_id");

  if (!userId) {
    return {
      status: "error",
      message: "User ID is required.",
    };
  }

  const response = await fetch(new URL(`/users/${userId}`, apiBaseUrl), {
    method: "DELETE",
    headers: getAuthHeaders(session.accessToken),
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

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
  const response = await fetch(new URL(path, apiBaseUrl), {
    method: "PATCH",
    headers: {
      ...getAuthHeaders(accessToken),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/sign-in");
  }

  return response;
}
