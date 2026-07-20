import { requestJson, type ApiRequestOptions } from "./client";
import type { NodeNetworkResponse } from "./node-network";
import type { NodeResponse } from "./node";

export type ReportRangingMeasurementRequest = {
  reported_by_device_id: string;
  pan_id: number;
  source_address: number;
  destination_address: number;
  distance: number;
};

export type RangingRecordResponse = {
  id: string;
  network: NodeNetworkResponse;
  listener_node: NodeResponse;
  initiator_node: NodeResponse;
  distance: number;
  recorded_at: string;
};

export type GetRangingRecordsQuery = {
  start: string;
  end: string;
  network_id?: string;
  node_id?: string;
};

export type GetLatestRangingRecordQuery = {
  network_id?: string;
  node_id?: string;
};

export type DeleteRangingRecordsQuery = GetRangingRecordsQuery;

export type DeleteRangingRecordsResponse = {
  deleted_count: number;
};

export function reportRangingMeasurement(
  request: ReportRangingMeasurementRequest,
  options?: ApiRequestOptions,
): Promise<RangingRecordResponse> {
  return requestJson<RangingRecordResponse>("/ranging/report", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function getRangingRecords(
  query: GetRangingRecordsQuery,
  options?: ApiRequestOptions,
): Promise<RangingRecordResponse[]> {
  return requestJson<RangingRecordResponse[]>("/ranging", {
    ...options,
    query,
  });
}

export function getLatestRangingRecord(
  query: GetLatestRangingRecordQuery = {},
  options?: ApiRequestOptions,
): Promise<RangingRecordResponse | null> {
  return requestJson<RangingRecordResponse | null>("/ranging/latest", {
    ...options,
    query,
  });
}

export function deleteRangingRecords(
  query: DeleteRangingRecordsQuery,
  options?: ApiRequestOptions,
): Promise<DeleteRangingRecordsResponse> {
  return requestJson<DeleteRangingRecordsResponse>("/ranging", {
    ...options,
    method: "DELETE",
    query,
  });
}
