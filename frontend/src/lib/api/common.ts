export type JsonObject = Record<string, unknown>;

export type ErrorResponse = {
  error: string;
};

export type MessageResponse = {
  message: string;
};

export type PaginationMeta = {
  page: number;
  limit: number;
  total: number;
};

export type PaginatedResponse<T> = {
  data: T[];
  meta: PaginationMeta;
};

export type PaginationQuery = {
  page?: number;
  limit?: number;
  cursor_id?: string;
  search?: string;
};

export type PermissionIdsRequest = {
  permission_ids: string[];
};
