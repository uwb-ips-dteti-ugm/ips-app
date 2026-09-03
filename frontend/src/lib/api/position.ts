import { requestJson, type ApiRequestOptions } from "./client";
import type { NodeNetworkResponse } from "./node-network";
import type { NodeResponse } from "./node";

export type ComputeTagPositionRequest = {
  tag_node_id: string;
  tag_height: number;
};

export type PositionRecordResponse = {
  id: string | null;
  network: NodeNetworkResponse;
  tag_node: NodeResponse;
  x: number;
  y: number;
  tag_height: number;
  computed_at: string;
};

export type GetPositionRecordsQuery = {
  start: string;
  end: string;
  network_id?: string;
  tag_node_id?: string;
};

export type GetLatestPositionRecordQuery = {
  network_id?: string;
  tag_node_id?: string;
};

export function computeTagPosition(
  request: ComputeTagPositionRequest,
  options?: ApiRequestOptions,
): Promise<PositionRecordResponse | null> {
  return requestJson<PositionRecordResponse | null>("/position/compute", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function getPositionRecords(
  query: GetPositionRecordsQuery,
  options?: ApiRequestOptions,
): Promise<PositionRecordResponse[]> {
  return requestJson<PositionRecordResponse[]>("/position", {
    ...options,
    query,
  });
}

export function getLatestPositionRecord(
  query: GetLatestPositionRecordQuery = {},
  options?: ApiRequestOptions,
): Promise<PositionRecordResponse | null> {
  return requestJson<PositionRecordResponse | null>("/position/latest", {
    ...options,
    query,
  });
}
