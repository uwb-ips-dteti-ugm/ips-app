import { requestJson, type ApiRequestOptions } from "./client";
import type {
  AuditedFields,
  JsonObject,
  MessageResponse,
  PaginatedResponse,
  PaginationQuery,
} from "./common";
import type { PermissionResponse } from "./permission";
import type { RoleResponse } from "./role";

export type UserStatus = "active" | "suspended" | "banned";

export type SetUserInfoRequest = {
  name?: string;
  bio?: string;
  username?: string;
};

export type SetUserRoleRequest = {
  role_id: string;
};

export type SetUserStatusRequest = {
  status: UserStatus;
};

export type UserResponse = AuditedFields & {
  id: string;
  name: string;
  username: string;
  bio: string;
  status: UserStatus;
  role: RoleResponse;
  preferences: JsonObject;
};

export type UsersResponse = PaginatedResponse<UserResponse>;

export type GetUsersQuery = PaginationQuery & {
  role_id?: string;
  status?: UserStatus;
};

export function getMyUser(options?: ApiRequestOptions): Promise<UserResponse> {
  return requestJson<UserResponse>("/users/me", options);
}

export function getMyPermissions(
  options?: ApiRequestOptions,
): Promise<PermissionResponse[]> {
  return requestJson<PermissionResponse[]>("/users/me/permissions", options);
}

export function updateMyUserInfo(
  request: SetUserInfoRequest,
  options?: ApiRequestOptions,
): Promise<UserResponse> {
  return requestJson<UserResponse>("/users/me/info", {
    ...options,
    json: request,
    method: "PATCH",
  });
}

export function updateMyUserPreferences(
  preferences: JsonObject,
  options?: ApiRequestOptions,
): Promise<UserResponse> {
  return requestJson<UserResponse>("/users/me/preferences", {
    ...options,
    json: preferences,
    method: "PATCH",
  });
}

export function getUsers(
  query: GetUsersQuery = {},
  options?: ApiRequestOptions,
): Promise<UsersResponse> {
  return requestJson<UsersResponse>("/users", {
    ...options,
    query,
  });
}

export function getUser(
  userId: string,
  options?: ApiRequestOptions,
): Promise<UserResponse> {
  return requestJson<UserResponse>(
    `/users/${encodeURIComponent(userId)}`,
    options,
  );
}

export function getUserPermissions(
  userId: string,
  options?: ApiRequestOptions,
): Promise<PermissionResponse[]> {
  return requestJson<PermissionResponse[]>(
    `/users/${encodeURIComponent(userId)}/permissions`,
    options,
  );
}

export function updateUserInfo(
  userId: string,
  request: SetUserInfoRequest,
  options?: ApiRequestOptions,
): Promise<UserResponse> {
  return requestJson<UserResponse>(
    `/users/${encodeURIComponent(userId)}/info`,
    {
      ...options,
      json: request,
      method: "PATCH",
    },
  );
}

export function updateUserPreferences(
  userId: string,
  preferences: JsonObject,
  options?: ApiRequestOptions,
): Promise<UserResponse> {
  return requestJson<UserResponse>(
    `/users/${encodeURIComponent(userId)}/preferences`,
    {
      ...options,
      json: preferences,
      method: "PATCH",
    },
  );
}

export function updateUserRole(
  userId: string,
  request: SetUserRoleRequest,
  options?: ApiRequestOptions,
): Promise<UserResponse> {
  return requestJson<UserResponse>(
    `/users/${encodeURIComponent(userId)}/role`,
    {
      ...options,
      json: request,
      method: "PATCH",
    },
  );
}

export function updateUserStatus(
  userId: string,
  request: SetUserStatusRequest,
  options?: ApiRequestOptions,
): Promise<UserResponse> {
  return requestJson<UserResponse>(
    `/users/${encodeURIComponent(userId)}/status`,
    {
      ...options,
      json: request,
      method: "PATCH",
    },
  );
}

export function deleteUser(
  userId: string,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>(`/users/${encodeURIComponent(userId)}`, {
    ...options,
    method: "DELETE",
  });
}
