import { requestJson, type ApiRequestOptions } from "./client";
import type { MessageResponse } from "./common";
import type { UserResponse } from "./user";

export type RegisterRequest = {
  name: string;
  username: string;
  password: string;
  role_id: string;
};

export type SignInRequest = {
  username: string;
  password: string;
};

export type RefreshTokenRequest = {
  refresh_token: string;
};

export type ChangeMyPasswordRequest = {
  old_password: string;
  new_password: string;
};

export type ResetUserPasswordRequest = {
  new_password: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
};

export function signIn(
  request: SignInRequest,
  options?: ApiRequestOptions,
): Promise<TokenResponse> {
  return requestJson<TokenResponse>("/auth/sign-in", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function refreshToken(
  request: RefreshTokenRequest,
  options?: ApiRequestOptions,
): Promise<TokenResponse> {
  return requestJson<TokenResponse>("/auth/refresh-token", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function register(
  request: RegisterRequest,
  options?: ApiRequestOptions,
): Promise<UserResponse> {
  return requestJson<UserResponse>("/auth/register", {
    ...options,
    json: request,
    method: "POST",
  });
}

export function updateMyPassword(
  request: ChangeMyPasswordRequest,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>("/auth/me/password", {
    ...options,
    json: request,
    method: "PATCH",
  });
}

export function resetUserPassword(
  userId: string,
  request: ResetUserPasswordRequest,
  options?: ApiRequestOptions,
): Promise<MessageResponse> {
  return requestJson<MessageResponse>(
    `/auth/${encodeURIComponent(userId)}/password`,
    {
      ...options,
      json: request,
      method: "PATCH",
    },
  );
}
