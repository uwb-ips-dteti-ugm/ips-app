import { requestJson, type ApiRequestOptions } from "./client";
import type { JsonObject } from "./common";

export type RecordLabel = "ranging" | "multilateration";

export type RecordDataRangingResponse = {
  distance: number;
  source_node_device_id: string;
  target_node_device_id: string;
};

export type MultilaterationCoordinateResponse = {
  node_device_id: string;
  x: number;
  y: number;
  z: number;
};

export type RecordDataMultilaterationResponse = {
  coordinates: MultilaterationCoordinateResponse[];
  ref_node_device_id: string;
};

export type RecordDataResponse =
  | RecordDataRangingResponse
  | RecordDataMultilaterationResponse;

export type RecordResponse = {
  data: RecordDataResponse;
  id: string | null;
  label: RecordLabel;
  metadata: JsonObject;
  recorded_at: string;
};

export type RecordsResponse = {
  data: RecordResponse[];
};

export type LatestRecordResponse = {
  data: RecordResponse | null;
};

export type RemovedRecordsResponse = {
  deleted_count: number;
};

export type RangingRecordsQuery = {
  end: string;
  source_node_device_ids?: string[];
  start: string;
  target_node_device_ids?: string[];
};

export type LatestRangingRecordQuery = {
  source_node_device_ids?: string[];
  target_node_device_ids?: string[];
};

export type MultilaterationRecordsQuery = {
  end: string;
  node_device_ids?: string[];
  ref_node_device_ids?: string[];
  start: string;
};

export type LatestMultilaterationRecordQuery = {
  node_device_ids?: string[];
  ref_node_device_ids?: string[];
};

export function getRangingRecords(
  query: RangingRecordsQuery,
  options?: ApiRequestOptions,
): Promise<RecordsResponse> {
  return requestJson<RecordsResponse>("/records/ranging", {
    ...options,
    query,
  });
}

export function getLatestRangingRecord(
  query: LatestRangingRecordQuery = {},
  options?: ApiRequestOptions,
): Promise<LatestRecordResponse> {
  return requestJson<LatestRecordResponse>("/records/ranging/latest", {
    ...options,
    query,
  });
}

export function deleteRangingRecords(
  request: RangingRecordsQuery,
  options?: ApiRequestOptions,
): Promise<RemovedRecordsResponse> {
  return requestJson<RemovedRecordsResponse>("/records/ranging", {
    ...options,
    json: request,
    method: "DELETE",
  });
}

export function getMultilaterationRecords(
  query: MultilaterationRecordsQuery,
  options?: ApiRequestOptions,
): Promise<RecordsResponse> {
  return requestJson<RecordsResponse>("/records/multilateration", {
    ...options,
    query,
  });
}

export function getLatestMultilaterationRecord(
  query: LatestMultilaterationRecordQuery = {},
  options?: ApiRequestOptions,
): Promise<LatestRecordResponse> {
  return requestJson<LatestRecordResponse>("/records/multilateration/latest", {
    ...options,
    query,
  });
}

export function deleteMultilaterationRecords(
  request: MultilaterationRecordsQuery,
  options?: ApiRequestOptions,
): Promise<RemovedRecordsResponse> {
  return requestJson<RemovedRecordsResponse>("/records/multilateration", {
    ...options,
    json: request,
    method: "DELETE",
  });
}

export function isRangingRecordData(
  data: RecordDataResponse,
): data is RecordDataRangingResponse {
  return (
    "source_node_device_id" in data &&
    "target_node_device_id" in data &&
    "distance" in data
  );
}
