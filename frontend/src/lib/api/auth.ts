import { requestJson, requestText, type ApiRequestOptions } from "./client";
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

export type SetPasswordAuthRequest =
  | {
      username: string;
      password?: string;
    }
  | {
      username?: string;
      password: string;
    };

export type SetPasswordAuthInfoRequest = {
  username: string;
};

export type SetPasswordWithOldPasswordRequest = {
  old_password: string;
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
  request: SetPasswordWithOldPasswordRequest,
  options?: ApiRequestOptions,
): Promise<string> {
  return requestText("/auth/me/password", {
    ...options,
    json: request,
    method: "PATCH",
  });
}

export function updateMyAuthInfo(
  request: SetPasswordAuthInfoRequest,
  options?: ApiRequestOptions,
): Promise<string> {
  return requestText("/auth/me/info", {
    ...options,
    json: request,
    method: "PATCH",
  });
}

export function updateUserPasswordAuth(
  userId: string,
  request: SetPasswordAuthRequest,
  options?: ApiRequestOptions,
): Promise<string> {
  return requestText(`/auth/${encodeURIComponent(userId)}/password-auth`, {
    ...options,
    json: request,
    method: "PATCH",
  });
}
