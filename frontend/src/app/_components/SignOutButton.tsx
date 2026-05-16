"use client";

import { useFormStatus } from "react-dom";

export function SignOutButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="h-10 rounded-md bg-[#0F2854] px-4 text-sm font-semibold text-white transition hover:bg-[#1C4D8D] disabled:cursor-not-allowed disabled:opacity-65 dark:bg-[#4988C4] dark:text-black dark:hover:bg-[#BDE8F5]"
    >
      {pending ? "Signing out" : "Sign out"}
    </button>
  );
}
