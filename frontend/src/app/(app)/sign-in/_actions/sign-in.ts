"use server";

import { redirect } from "next/navigation";

import { signIn } from "@/lib/api/auth";
import { isApiError } from "@/lib/api/client";
import { getSafeRedirectPath } from "@/lib/auth/redirect";
import { setAuthCookies } from "@/lib/auth/session";

export type SignInFormState = {
  error: string | null;
  fieldError: SignInFieldError;
};

export type SignInFieldError = "credentials" | "password" | "username" | null;

export async function signInAction(
  _previousState: SignInFormState,
  formData: FormData,
): Promise<SignInFormState> {
  const username = String(formData.get("username") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  const callbackUrl = getSafeRedirectPath(formData.get("callbackUrl"));

  if (!username && !password) {
    return {
      error: "Username and password are required.",
      fieldError: "credentials",
    };
  }

  if (!username) {
    return {
      error: "Username is required.",
      fieldError: "username",
    };
  }

  if (!password) {
    return {
      error: "Password is required.",
      fieldError: "password",
    };
  }

  try {
    const tokens = await signIn({
      username,
      password,
    });

    await setAuthCookies(tokens);
  } catch (error) {
    const errorMessage = isApiError(error)
      ? error.message
      : "The sign-in service is unavailable. Please try again.";

    return {
      error: errorMessage,
      fieldError: getFieldError(errorMessage),
    };
  }

  redirect(callbackUrl);
}

function getFieldError(message: string): SignInFieldError {
  const normalizedMessage = message.toLowerCase();

  if (normalizedMessage.includes("username")) {
    return "username";
  }

  if (normalizedMessage.includes("password")) {
    return "password";
  }

  return null;
}
