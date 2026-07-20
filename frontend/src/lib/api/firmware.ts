import { requestJson, type ApiRequestOptions } from "./client";
import type { AuditedFields, MessageResponse, PaginatedResponse, PaginationQuery } from "./common";

export type FirmwareResponse = AuditedFields & {
  id: string;
  version: string;
  board_variant: string;
  size: number;
  checksum: string;
};

export type FirmwareDeployResponse = {
  targeted_count: number;
  succeeded_count: number;
  failed_device_ids: string[];
};

export function getFirmwares(
  query: PaginationQuery,
  options?: ApiRequestOptions,
): Promise<PaginatedResponse<FirmwareResponse>> {
  return requestJson<PaginatedResponse<FirmwareResponse>>("/firmware", {
    ...options,
    query,
  });
}

export function deleteFirmware(
  firmwareId: string,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>(`/firmware/${firmwareId}`, {
    ...options,
    method: "DELETE",
  });
}

export function deployFirmware(
  firmwareId: string,
  options?: ApiRequestOptions,
): Promise<FirmwareDeployResponse> {
  return requestJson<FirmwareDeployResponse>(`/firmware/${firmwareId}/deploy`, {
    ...options,
    method: "POST",
  });
}
