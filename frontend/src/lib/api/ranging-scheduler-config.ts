import { requestJson, type ApiRequestOptions } from "./client";
import type { AuditedFields } from "./common";

export type UpdateRangingSchedulerConfigRequest = {
  listen_timeout_uus?: number;
  initiate_timeout_uus?: number;
  listen_to_initiate_delay_ms?: number;
  pair_delay_ms?: number;
  idle_delay_ms?: number;
};

export type RangingSchedulerConfigResponse = AuditedFields & {
  id: string;
  listen_timeout_uus: number;
  initiate_timeout_uus: number;
  listen_to_initiate_delay_ms: number;
  pair_delay_ms: number;
  idle_delay_ms: number;
};

export function getRangingSchedulerConfig(
  options?: ApiRequestOptions,
): Promise<RangingSchedulerConfigResponse> {
  return requestJson<RangingSchedulerConfigResponse>(
    "/ranging-scheduler-config",
    options,
  );
}

export function updateRangingSchedulerConfig(
  request: UpdateRangingSchedulerConfigRequest,
  options?: ApiRequestOptions,
): Promise<RangingSchedulerConfigResponse> {
  return requestJson<RangingSchedulerConfigResponse>(
    "/ranging-scheduler-config",
    {
      ...options,
      json: request,
      method: "PATCH",
    },
  );
}

export function resetRangingSchedulerConfig(
  options?: ApiRequestOptions,
): Promise<RangingSchedulerConfigResponse> {
  return requestJson<RangingSchedulerConfigResponse>(
    "/ranging-scheduler-config/reset",
    {
      ...options,
      method: "POST",
    },
  );
}
