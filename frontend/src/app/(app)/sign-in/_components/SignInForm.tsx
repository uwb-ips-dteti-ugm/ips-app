"use client";

import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { useActionState, useEffect, useRef, useState } from "react";

import eyeIcon from "@/shared/assets/EyeIcon.svg";
import eyeOffIcon from "@/shared/assets/EyeOffIcon.svg";
import { useErrorToast } from "@/shared/components/ErrorToast";

import { signInAction, type SignInFormState } from "../_actions/sign-in";
import { SubmitButton } from "./SubmitButton";

const initialState: SignInFormState = {
  error: null,
  fieldError: null,
};

export function SignInForm() {
  const searchParams = useSearchParams();
  const passwordInputRef = useRef<HTMLInputElement>(null);
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [usernameValue, setUsernameValue] = useState("");
  const [state, formAction] = useActionState(signInAction, initialState);
  const { showError } = useErrorToast();
  const callbackUrl = getCallbackUrl(searchParams.get("callbackUrl"));
  const hasUsernameError =
    state.fieldError === "username" || state.fieldError === "credentials";
  const hasPasswordError =
    state.fieldError === "password" || state.fieldError === "credentials";

  useEffect(() => {
    if (state.error) {
      showError({
        title: "Sign-in failed",
        message: state.error,
      });
    }
  }, [showError, state]);

  useEffect(() => {
    if (state.fieldError === "password") {
      if (passwordInputRef.current) {
        passwordInputRef.current.value = "";
      }
      passwordInputRef.current?.focus();
    }
  }, [state]);

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <input type="hidden" name="callbackUrl" value={callbackUrl} />

      <div className="flex flex-col gap-2">
        <label
          htmlFor="sign-in-username"
          className="text-sm font-medium text-[#0F2854] dark:text-white"
        >
          Username
        </label>
        <input
          id="sign-in-username"
          name="username"
          type="text"
          autoComplete="username"
          required
          aria-invalid={hasUsernameError}
          value={usernameValue}
          onChange={(event) => setUsernameValue(event.currentTarget.value)}
          className={getInputClassName(hasUsernameError)}
        />
      </div>

      <div className="flex flex-col gap-2">
        <label
          htmlFor="sign-in-password"
          className="text-sm font-medium text-[#0F2854] dark:text-white"
        >
          Password
        </label>
        <div className="relative">
          <input
            id="sign-in-password"
            name="password"
            type={isPasswordVisible ? "text" : "password"}
            autoComplete="current-password"
            required
            aria-invalid={hasPasswordError}
            ref={passwordInputRef}
            className={`${getInputClassName(hasPasswordError)} pr-10`}
          />
          <button
            type="button"
            aria-label={isPasswordVisible ? "Hide password" : "Show password"}
            aria-pressed={isPasswordVisible}
            onClick={() => setIsPasswordVisible((current) => !current)}
            className="absolute right-2 top-1/2 inline-flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md transition hover:bg-[#BDE8F5]/45 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] dark:hover:bg-[#1C4D8D]/55"
          >
            <Image
              src={isPasswordVisible ? eyeOffIcon : eyeIcon}
              alt=""
              width={18}
              height={18}
            />
          </button>
        </div>
      </div>

      <SubmitButton />
    </form>
  );
}

function getInputClassName(hasError: boolean): string {
  const baseClassName =
    "h-11 w-full rounded-md border bg-white px-3 text-base text-black outline-none transition focus:ring-4 dark:bg-black dark:text-white";

  if (hasError) {
    return `${baseClassName} border-[#D85858] focus:border-[#D85858] focus:ring-[#F3B7B7]/70 dark:border-[#E05A5A] dark:focus:ring-[#E05A5A]/25`;
  }

  return `${baseClassName} border-[#C8DDEB] focus:border-[#4988C4] focus:ring-[#BDE8F5]/60 dark:border-[#1C4D8D] dark:focus:ring-[#4988C4]/25`;
}

function getCallbackUrl(value: string | null): string {
  if (value && value.startsWith("/") && !value.startsWith("//")) {
    return value;
  }

  return "/";
}
