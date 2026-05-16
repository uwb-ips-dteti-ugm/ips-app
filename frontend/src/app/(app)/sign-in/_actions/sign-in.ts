"use server";

import { redirect } from "next/navigation";

import { setAuthCookies } from "@/lib/auth/session";
import { getSafeRedirectPath } from "@/lib/auth/redirect";

type BackendTokenResponse = {
  access_token: string;
  refresh_token: string;
};

export type SignInFormState = {
  error: string | null;
};

const apiBaseUrl =
  process.env.IPS_API_BASE_URL ??
  process.env.NEXT_PUBLIC_IPS_API_BASE_URL ??
  "http://localhost:8000";

export async function signInAction(
  _previousState: SignInFormState,
  formData: FormData,
): Promise<SignInFormState> {
  const signInIdentifier = String(
    formData.get("sign_in_identifier") ?? "",
  ).trim();
  const password = String(formData.get("password") ?? "");
  const callbackUrl = getSafeRedirectPath(formData.get("callbackUrl"));

  if (!signInIdentifier || !password) {
    return {
      error: "Username and password are required.",
    };
  }

  let tokens: BackendTokenResponse;
  try {
    const response = await fetch(`${apiBaseUrl}/auth/sign-in`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sign_in_identifier: signInIdentifier,
        password,
      }),
      cache: "no-store",
    });

    if (!response.ok) {
      return {
        error: "Invalid username or password.",
      };
    }

    tokens = (await response.json()) as BackendTokenResponse;
  } catch {
    return {
      error: "Sign-in service is unavailable.",
    };
  }

  await setAuthCookies(tokens);
  redirect(callbackUrl);
}
