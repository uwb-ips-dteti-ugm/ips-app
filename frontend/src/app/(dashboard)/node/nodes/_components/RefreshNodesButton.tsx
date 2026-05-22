"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useTransition } from "react";

import refreshIcon from "@/shared/assets/RefreshIcon.svg";

export function RefreshNodesButton() {
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  return (
    <button
      type="button"
      disabled={pending}
      onClick={() => {
        startTransition(() => {
          router.refresh();
        });
      }}
      className="inline-flex h-10 items-center justify-center gap-2 whitespace-nowrap rounded-md bg-[#0F2854] px-4 text-sm font-semibold text-white transition hover:bg-[#1C4D8D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] disabled:cursor-wait disabled:opacity-60 dark:bg-[#4988C4] dark:hover:bg-[#1C4D8D]"
    >
      <Image
        src={refreshIcon}
        alt=""
        width={16}
        height={16}
        className={pending ? "animate-spin" : ""}
      />
      <span>{pending ? "Refreshing" : "Refresh"}</span>
    </button>
  );
}
