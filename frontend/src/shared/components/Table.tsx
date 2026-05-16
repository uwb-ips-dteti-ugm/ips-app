"use client";

import Image, { type StaticImageData } from "next/image";
import { type ReactNode } from "react";

type DataTableProps = {
  children: ReactNode;
};

type IconActionButtonProps = {
  icon: StaticImageData;
  label: string;
  onClick: () => void;
  variant?: "default" | "danger";
};

export function DataTable({ children }: DataTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
        {children}
      </table>
    </div>
  );
}

export function TableHead({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <th
      className={`whitespace-nowrap px-4 py-3 text-center font-semibold ${className}`}
    >
      {children}
    </th>
  );
}

export function TableCell({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <td
      className={`border-b border-[#D9EEF7] px-4 py-3 align-middle text-[#0F2854] last:border-b dark:border-[#1C4D8D] dark:text-white ${className}`}
    >
      {children}
    </td>
  );
}

export function TableBadge({
  children,
  className,
}: {
  children: ReactNode;
  className: string;
}) {
  return (
    <span
      className={`inline-flex h-7 items-center rounded-md border px-2.5 text-xs font-semibold ${className}`}
    >
      {children}
    </span>
  );
}

export function EmptyTableState({ message }: { message: string }) {
  return (
    <div className="border-t border-[#D9EEF7] px-4 py-10 text-center text-sm text-[#4988C4] dark:border-[#1C4D8D] dark:text-[#BDE8F5]">
      {message}
    </div>
  );
}

export function RowActions({ children }: { children: ReactNode }) {
  return <div className="flex justify-center gap-2">{children}</div>;
}

export function IconActionButton({
  icon,
  label,
  onClick,
  variant = "default",
}: IconActionButtonProps) {
  const isDanger = variant === "danger";

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      className={
        isDanger
          ? "group relative inline-flex h-9 w-9 items-center justify-center rounded-md border border-[#E05A5A] bg-transparent text-[#E05A5A] transition hover:bg-[#E05A5A] hover:text-white"
          : "group relative inline-flex h-9 w-9 items-center justify-center rounded-md border border-[#4988C4] text-[#1C4D8D] transition hover:bg-[#BDE8F5]/50 dark:text-[#BDE8F5] dark:hover:bg-[#1C4D8D]/50"
      }
    >
      <Image
        src={icon}
        alt=""
        width={16}
        height={16}
        className={
          isDanger
            ? "h-4 w-4 shrink-0 transition group-hover:brightness-0 group-hover:invert"
            : "h-4 w-4 shrink-0 dark:brightness-0 dark:invert"
        }
      />
      <span className="pointer-events-none absolute bottom-full left-1/2 mb-2 -translate-x-1/2 whitespace-nowrap rounded-md bg-[#0F2854] px-2 py-1 text-xs font-semibold text-white opacity-0 shadow-sm transition group-hover:opacity-100 group-focus-visible:opacity-100 dark:bg-[#BDE8F5] dark:text-[#07111F]">
        {label}
      </span>
    </button>
  );
}

export function TableLoadingOverlay({ label }: { label: string }) {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/75 backdrop-blur-[1px] dark:bg-[#07111F]/75">
      <div className="flex min-w-44 flex-col gap-2 rounded-md border border-[#D9EEF7] bg-white px-4 py-3 shadow-sm dark:border-[#1C4D8D] dark:bg-[#07111F]">
        <div className="h-1.5 overflow-hidden rounded-full bg-[#BDE8F5] dark:bg-[#1C4D8D]">
          <div className="h-full w-2/3 animate-[shared-loading-bar_1s_ease-in-out_infinite] rounded-full bg-[#1C4D8D] dark:bg-[#BDE8F5]" />
        </div>
        <div className="text-center text-xs font-semibold uppercase text-[#1C4D8D] dark:text-[#BDE8F5]">
          {label}
        </div>
      </div>
      <style jsx>{`
        @keyframes shared-loading-bar {
          0% {
            transform: translateX(-110%);
          }
          100% {
            transform: translateX(160%);
          }
        }
      `}</style>
    </div>
  );
}
