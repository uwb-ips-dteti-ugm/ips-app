"use client";

import { useActionState } from "react";
import { useSearchParams } from "next/navigation";

import { signInAction, type SignInFormState } from "../_actions/sign-in";
import { SubmitButton } from "./SubmitButton";

const initialState: SignInFormState = {
  error: null,
};

export function SignInForm() {
  const searchParams = useSearchParams();
  const [state, formAction] = useActionState(signInAction, initialState);
  const callbackUrl = getCallbackUrl(searchParams.get("callbackUrl"));

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <input type="hidden" name="callbackUrl" value={callbackUrl} />

      <div className="flex flex-col gap-2">
        <label
          htmlFor="sign-in-identifier"
          className="text-sm font-medium text-[#0F2854] dark:text-white"
        >
          Username
        </label>
        <input
          id="sign-in-identifier"
          name="sign_in_identifier"
          type="text"
          autoComplete="username"
          required
          className="h-11 rounded-md border border-[#C8DDEB] bg-white px-3 text-base text-black outline-none transition focus:border-[#4988C4] focus:ring-4 focus:ring-[#BDE8F5]/60 dark:border-[#1C4D8D] dark:bg-black dark:text-white dark:focus:ring-[#4988C4]/25"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label
          htmlFor="sign-in-password"
          className="text-sm font-medium text-[#0F2854] dark:text-white"
        >
          Password
        </label>
        <input
          id="sign-in-password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          className="h-11 rounded-md border border-[#C8DDEB] bg-white px-3 text-base text-black outline-none transition focus:border-[#4988C4] focus:ring-4 focus:ring-[#BDE8F5]/60 dark:border-[#1C4D8D] dark:bg-black dark:text-white dark:focus:ring-[#4988C4]/25"
        />
      </div>

      {state.error ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-200"
        >
          {state.error}
        </p>
      ) : null}

      <SubmitButton />
    </form>
  );
}

function getCallbackUrl(value: string | null): string {
  if (value && value.startsWith("/") && !value.startsWith("//")) {
    return value;
  }

  return "/";
}
