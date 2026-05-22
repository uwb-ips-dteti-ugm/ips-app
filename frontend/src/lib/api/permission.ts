import { requestJson, type ApiRequestOptions } from "./client";
import type {
  JsonObject,
  MessageResponse,
  PaginatedResponse,
  PaginationQuery,
} from "./common";

export type AddPermissionRequest = {
  name: string;
  description?: string;
};

export type SetPermissionRequest = {
  name?: string;
  description?: string;
};

export type PermissionResponse = {
  id: string;
  name: string;
  description: string;
  preferences: JsonObject;
  created_at: string;
  updated_at: string | null;
};

export type PermissionsResponse = PaginatedResponse<PermissionResponse>;

export type GetPermissionsQuery = PaginationQuery;

export function createPermission(
  request: AddPermissionRequest,
  options?: ApiRequestOptions,
): Promise<PermissionResponse> {
  return requestJson<PermissionResponse>("/permissions", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function getPermissions(
  query: GetPermissionsQuery = {},
  options?: ApiRequestOptions,
): Promise<PermissionsResponse> {
  return requestJson<PermissionsResponse>("/permissions", {
    ...options,
    query,
  });
}

export function getPermission(
  permissionId: string,
  options?: ApiRequestOptions,
): Promise<PermissionResponse> {
  return requestJson<PermissionResponse>(
    `/permissions/${encodeURIComponent(permissionId)}`,
    options,
  );
}

export function updatePermission(
  permissionId: string,
  request: SetPermissionRequest,
  options?: ApiRequestOptions,
): Promise<PermissionResponse> {
  return requestJson<PermissionResponse>(
    `/permissions/${encodeURIComponent(permissionId)}`,
    {
      ...options,
      json: request,
      method: "PATCH",
    },
  );
}

export function updatePermissionPreferences(
  permissionId: string,
  preferences: JsonObject,
  options?: ApiRequestOptions,
): Promise<PermissionResponse> {
  return requestJson<PermissionResponse>(
    `/permissions/${encodeURIComponent(permissionId)}/preferences`,
    {
      ...options,
      json: preferences,
      method: "PATCH",
    },
  );
}

export function deletePermission(
  permissionId: string,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>(
    `/permissions/${encodeURIComponent(permissionId)}`,
    {
      ...options,
      method: "DELETE",
    },
  );
}
