export type JsonObject = Record<string, unknown>;

export type ErrorResponse = {
  error: string;
};

export type MessageResponse = {
  message: string;
};

export type AuditedFields = {
  created_at: string;
  created_by: string | null;
  updated_at: string | null;
  updated_by: string | null;
};

export type PaginatedResponse<T> = {
  items: T[];
  page: number;
  limit: number;
  total: number;
};

export type PaginationQuery = {
  page?: number;
  limit?: number;
  search?: string;
};

export type PermissionIdsRequest = {
  permission_ids: string[];
};
