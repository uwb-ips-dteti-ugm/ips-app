import { requestJson, type ApiRequestOptions } from "./client";
import type {
  AuditedFields,
  MessageResponse,
  PaginatedResponse,
  PaginationQuery,
} from "./common";

export type AddNodeNetworkRequest = {
  pan_id: number;
  name: string;
  description?: string;
};

export type SetNodeNetworkRequest = {
  pan_id?: number;
  name?: string;
  description?: string;
};

export type NodeNetworkResponse = AuditedFields & {
  id: string;
  pan_id: number;
  name: string;
  description: string;
};

export type NodeNetworksResponse = PaginatedResponse<NodeNetworkResponse>;

export type GetNodeNetworksQuery = PaginationQuery;

export function createNodeNetwork(
  request: AddNodeNetworkRequest,
  options?: ApiRequestOptions,
): Promise<NodeNetworkResponse> {
  return requestJson<NodeNetworkResponse>("/node-networks", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function getNodeNetworks(
  query: GetNodeNetworksQuery = {},
  options?: ApiRequestOptions,
): Promise<NodeNetworksResponse> {
  return requestJson<NodeNetworksResponse>("/node-networks", {
    ...options,
    query,
  });
}

export function getNodeNetworkByPanId(
  panId: number,
  options?: ApiRequestOptions,
): Promise<NodeNetworkResponse> {
  return requestJson<NodeNetworkResponse>(
    `/node-networks/pan/${encodeURIComponent(String(panId))}`,
    options,
  );
}

export function getNodeNetwork(
  nodeNetworkId: string,
  options?: ApiRequestOptions,
): Promise<NodeNetworkResponse> {
  return requestJson<NodeNetworkResponse>(
    `/node-networks/${encodeURIComponent(nodeNetworkId)}`,
    options,
  );
}

export function updateNodeNetwork(
  nodeNetworkId: string,
  request: SetNodeNetworkRequest,
  options?: ApiRequestOptions,
): Promise<NodeNetworkResponse> {
  return requestJson<NodeNetworkResponse>(
    `/node-networks/${encodeURIComponent(nodeNetworkId)}`,
    {
      ...options,
      json: request,
      method: "PATCH",
    },
  );
}

export function deleteNodeNetwork(
  nodeNetworkId: string,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>(
    `/node-networks/${encodeURIComponent(nodeNetworkId)}`,
    {
      ...options,
      method: "DELETE",
    },
  );
}
