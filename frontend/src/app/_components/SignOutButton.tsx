"use client";

import Image from "next/image";
import { useFormStatus } from "react-dom";

import exitIcon from "../_assets/ExitIcon.svg";

export function SignOutButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="group flex h-10 w-full items-center justify-center gap-2 rounded-md border border-[#E05A5A] bg-transparent px-4 text-sm font-semibold text-[#E05A5A] transition hover:bg-[#E05A5A] hover:text-white disabled:cursor-not-allowed disabled:opacity-65"
    >
      <Image
        src={exitIcon}
        alt=""
        width={18}
        height={18}
        className="h-4.5 w-4.5 shrink-0 transition group-hover:brightness-0 group-hover:invert"
      />
      {pending ? "Signing out" : "Sign out"}
    </button>
  );
}
