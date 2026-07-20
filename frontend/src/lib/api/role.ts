import { requestJson, type ApiRequestOptions } from "./client";
import type {
  AuditedFields,
  JsonObject,
  MessageResponse,
  PaginatedResponse,
  PaginationQuery,
  PermissionIdsRequest,
} from "./common";
import type { PermissionResponse } from "./permission";

export type AddRoleRequest = {
  name: string;
  description?: string;
  is_default?: boolean;
};

export type SetRoleRequest = {
  name?: string;
  description?: string;
};

export type RoleResponse = AuditedFields & {
  id: string;
  name: string;
  description: string;
  is_default: boolean;
  permissions: PermissionResponse[];
  preferences: JsonObject;
};

export type RolesResponse = PaginatedResponse<RoleResponse>;

export type GetRolesQuery = PaginationQuery;

export function createRole(
  request: AddRoleRequest,
  options?: ApiRequestOptions,
): Promise<RoleResponse> {
  return requestJson<RoleResponse>("/roles", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function getRoles(
  query: GetRolesQuery = {},
  options?: ApiRequestOptions,
): Promise<RolesResponse> {
  return requestJson<RolesResponse>("/roles", {
    ...options,
    query,
  });
}

export function getDefaultRole(
  options?: ApiRequestOptions,
): Promise<RoleResponse> {
  return requestJson<RoleResponse>("/roles/default", options);
}

export function getRole(
  roleId: string,
  options?: ApiRequestOptions,
): Promise<RoleResponse> {
  return requestJson<RoleResponse>(
    `/roles/${encodeURIComponent(roleId)}`,
    options,
  );
}

export function updateRole(
  roleId: string,
  request: SetRoleRequest,
  options?: ApiRequestOptions,
): Promise<RoleResponse> {
  return requestJson<RoleResponse>(`/roles/${encodeURIComponent(roleId)}`, {
    ...options,
    json: request,
    method: "PATCH",
  });
}

export function setDefaultRole(
  roleId: string,
  options?: ApiRequestOptions,
): Promise<RoleResponse> {
  return requestJson<RoleResponse>(
    `/roles/${encodeURIComponent(roleId)}/default`,
    {
      ...options,
      method: "PATCH",
    },
  );
}

export function updateRolePreferences(
  roleId: string,
  preferences: JsonObject,
  options?: ApiRequestOptions,
): Promise<RoleResponse> {
  return requestJson<RoleResponse>(
    `/roles/${encodeURIComponent(roleId)}/preferences`,
    {
      ...options,
      json: preferences,
      method: "PATCH",
    },
  );
}

export function deleteRole(
  roleId: string,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>(`/roles/${encodeURIComponent(roleId)}`, {
    ...options,
    method: "DELETE",
  });
}

export function addRolePermissions(
  roleId: string,
  request: PermissionIdsRequest,
  options?: ApiRequestOptions,
): Promise<RoleResponse> {
  return requestJson<RoleResponse>(
    `/roles/${encodeURIComponent(roleId)}/permissions`,
    {
      ...options,
      json: request,
      method: "POST",
    },
  );
}

export function removeRolePermissions(
  roleId: string,
  request: PermissionIdsRequest,
  options?: ApiRequestOptions,
): Promise<RoleResponse> {
  return requestJson<RoleResponse>(
    `/roles/${encodeURIComponent(roleId)}/permissions`,
    {
      ...options,
      json: request,
      method: "DELETE",
    },
  );
}

export function getRolePermissions(
  roleId: string,
  options?: ApiRequestOptions,
): Promise<PermissionResponse[]> {
  return requestJson<PermissionResponse[]>(
    `/roles/${encodeURIComponent(roleId)}/permissions`,
    options,
  );
}
