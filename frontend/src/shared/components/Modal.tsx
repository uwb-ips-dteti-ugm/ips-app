"use client";

import Image from "next/image";
import { type ReactNode, useEffect, useId } from "react";

import closeIcon from "../assets/CloseIcon.svg";

type ModalProps = {
  children: ReactNode;
  onClose: () => void;
  title: string;
  widthClassName?: string;
};

type ModalActionsProps = {
  destructive?: boolean;
  onClose: () => void;
  pending: boolean;
  pendingLabel: string;
  submitDisabled?: boolean;
  submitLabel: string;
};

export function Modal({
  children,
  onClose,
  title,
  widthClassName = "max-w-lg",
}: ModalProps) {
  const titleId = useId();

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center p-4">
      <button
        type="button"
        aria-label="Close modal"
        className="absolute inset-0 cursor-default bg-[#07111F]/55 backdrop-blur-sm"
        onClick={onClose}
      />
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={`relative max-h-[calc(100dvh-2rem)] w-full ${widthClassName} overflow-y-auto rounded-md border border-[#D9EEF7] bg-white shadow-xl dark:border-[#1C4D8D] dark:bg-[#07111F]`}
      >
        <header className="flex items-center justify-between border-b border-[#D9EEF7] px-5 py-4 dark:border-[#1C4D8D]">
          <h2
            id={titleId}
            className="text-lg font-semibold text-[#0F2854] dark:text-white"
          >
            {title}
          </h2>
          <button
            type="button"
            aria-label="Close modal"
            className="inline-flex h-8 w-8 items-center justify-center rounded-md transition hover:bg-[#BDE8F5]/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] dark:hover:bg-[#1C4D8D]/50"
            onClick={onClose}
          >
            <Image
              src={closeIcon}
              alt=""
              width={16}
              height={16}
              className="shrink-0 dark:brightness-0 dark:invert"
            />
          </button>
        </header>
        <div className="px-5 py-5">{children}</div>
      </section>
    </div>
  );
}

export function ModalActions({
  destructive = false,
  onClose,
  pending,
  pendingLabel,
  submitDisabled = false,
  submitLabel,
}: ModalActionsProps) {
  return (
    <div className="flex flex-wrap justify-end gap-2 border-t border-[#D9EEF7] pt-4 dark:border-[#1C4D8D]">
      <button
        type="button"
        disabled={pending}
        className="inline-flex h-10 items-center justify-center rounded-md border border-[#D9EEF7] bg-white px-4 text-sm font-semibold text-[#0F2854] transition hover:bg-[#BDE8F5]/35 disabled:cursor-not-allowed disabled:opacity-60 dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-[#BDE8F5] dark:hover:bg-[#1C4D8D]/40"
        onClick={onClose}
      >
        Cancel
      </button>
      <button
        type="submit"
        disabled={pending || submitDisabled}
        className={
          destructive
            ? "inline-flex h-10 items-center justify-center rounded-md bg-[#D85858] px-4 text-sm font-semibold text-white transition hover:bg-[#C84646] disabled:cursor-not-allowed disabled:opacity-60"
            : "inline-flex h-10 items-center justify-center rounded-md bg-[#0F2854] px-4 text-sm font-semibold text-white transition hover:bg-[#1C4D8D] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#4988C4] dark:hover:bg-[#1C4D8D]"
        }
      >
        {pending ? pendingLabel : submitLabel}
      </button>
    </div>
  );
}
