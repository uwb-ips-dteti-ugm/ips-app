import { requestJson, type ApiRequestOptions } from "./client";
import type {
  JsonObject,
  MessageResponse,
  PaginatedResponse,
  PaginationQuery,
} from "./common";
import type { NodeNetworkResponse } from "./node-network";

export type NodeStatus = "pending" | "approved" | "suspended" | "revoked";

export type AddNodeRequest = {
  address?: number;
  description?: string;
  device_id: string;
  name: string;
  network_id?: string;
  preferences?: JsonObject;
};

export type SetNodeInfoRequest = {
  description?: string;
  name?: string;
};

export type SetNodeNetworkAssignmentRequest = {
  address?: number | null;
  network_id?: string | null;
};

export type SetNodeStatusRequest = {
  status: NodeStatus;
};

export type AddRangingRecordByAddressesRequest = {
  destination_address: number;
  distance: number;
  pan_id: number;
  reported_by_device_id: string;
  source_address: number;
};

export type NodeResponse = {
  address: number | null;
  approved_at: string | null;
  approved_by: string | null;
  created_at: string;
  description: string;
  device_id: string;
  id: string;
  is_approved: boolean;
  last_connected_at: string | null;
  last_disconnected_at: string | null;
  last_seen_at: string | null;
  name: string;
  network: NodeNetworkResponse | null;
  preferences: JsonObject;
  status: NodeStatus;
  updated_at: string | null;
};

export type NodesResponse = PaginatedResponse<NodeResponse>;

export type GetNodesQuery = PaginationQuery & {
  address?: number;
  is_online?: boolean;
  network_id?: string;
  status?: NodeStatus;
};

export type NodeRegistrationResponse = {
  device_id: string;
  is_registered: boolean;
};

export type RegisteredNodesResponse = {
  data: string[];
};

export function createNode(
  request: AddNodeRequest,
  options?: ApiRequestOptions,
): Promise<NodeResponse> {
  return requestJson<NodeResponse>("/nodes", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function getNodes(
  query: GetNodesQuery = {},
  options?: ApiRequestOptions,
): Promise<NodesResponse> {
  return requestJson<NodesResponse>("/nodes", {
    ...options,
    query,
  });
}

export function getRegisteredNodes(
  options?: ApiRequestOptions,
): Promise<RegisteredNodesResponse> {
  return requestJson<RegisteredNodesResponse>("/nodes/registered", options);
}

export function getNodeRegistration(
  deviceId: string,
  options?: ApiRequestOptions,
): Promise<NodeRegistrationResponse> {
  return requestJson<NodeRegistrationResponse>(
    `/nodes/registered/${encodeURIComponent(deviceId)}`,
    options,
  );
}

export function getNodeByDeviceId(
  deviceId: string,
  options?: ApiRequestOptions,
): Promise<NodeResponse> {
  return requestJson<NodeResponse>(
    `/nodes/device/${encodeURIComponent(deviceId)}`,
    options,
  );
}

export function restartNode(
  deviceId: string,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>(
    `/nodes/device/${encodeURIComponent(deviceId)}/restart`,
    {
      ...options,
      method: "POST",
    },
  );
}

export function getNodeByNetworkAddress(
  networkId: string,
  address: number,
  options?: ApiRequestOptions,
): Promise<NodeResponse> {
  return requestJson<NodeResponse>(
    `/nodes/network/${encodeURIComponent(networkId)}/address/${encodeURIComponent(String(address))}`,
    options,
  );
}

export function addRangingRecordByAddresses(
  request: AddRangingRecordByAddressesRequest,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>("/nodes/ranging-records", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function getNode(
  nodeId: string,
  options?: ApiRequestOptions,
): Promise<NodeResponse> {
  return requestJson<NodeResponse>(`/nodes/${encodeURIComponent(nodeId)}`, options);
}

export function updateNodeInfo(
  nodeId: string,
  request: SetNodeInfoRequest,
  options?: ApiRequestOptions,
): Promise<NodeResponse> {
  return requestJson<NodeResponse>(`/nodes/${encodeURIComponent(nodeId)}/info`, {
    ...options,
    json: request,
    method: "PATCH",
  });
}

export function updateNodeNetworkAssignment(
  nodeId: string,
  request: SetNodeNetworkAssignmentRequest,
  options?: ApiRequestOptions,
): Promise<NodeResponse> {
  return requestJson<NodeResponse>(
    `/nodes/${encodeURIComponent(nodeId)}/network`,
    {
      ...options,
      json: request,
      method: "PATCH",
    },
  );
}

export function updateNodePreferences(
  nodeId: string,
  preferences: JsonObject,
  options?: ApiRequestOptions,
): Promise<NodeResponse> {
  return requestJson<NodeResponse>(
    `/nodes/${encodeURIComponent(nodeId)}/preferences`,
    {
      ...options,
      json: preferences,
      method: "PATCH",
    },
  );
}

export function updateNodeStatus(
  nodeId: string,
  request: SetNodeStatusRequest,
  options?: ApiRequestOptions,
): Promise<NodeResponse> {
  return requestJson<NodeResponse>(
    `/nodes/${encodeURIComponent(nodeId)}/status`,
    {
      ...options,
      json: request,
      method: "PATCH",
    },
  );
}

export function deleteNode(
  nodeId: string,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>(`/nodes/${encodeURIComponent(nodeId)}`, {
    ...options,
    method: "DELETE",
  });
}
