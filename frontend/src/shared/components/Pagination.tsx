"use client";

type PaginationProps = {
  busy?: boolean;
  hasNext: boolean;
  hasPrevious: boolean;
  itemCount: number;
  itemLabel: string;
  onNext: () => void;
  onPrevious: () => void;
};

export function Pagination({
  busy = false,
  hasNext,
  hasPrevious,
  itemCount,
  itemLabel,
  onNext,
  onPrevious,
}: PaginationProps) {
  return (
    <div
      aria-busy={busy}
      className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-t border-[#D9EEF7] px-4 py-3 text-sm text-[#1C4D8D] dark:border-[#1C4D8D] dark:text-[#BDE8F5]"
    >
      <span>
        Showing{" "}
        <span className="font-semibold text-[#0F2854] dark:text-white">
          {itemCount}
        </span>{" "}
        {itemCount === 1 ? itemLabel : `${itemLabel}s`}
      </span>

      <div className="flex items-center gap-2">
        <button
          type="button"
          disabled={!hasPrevious || busy}
          onClick={onPrevious}
          className="inline-flex h-9 items-center justify-center rounded-md border border-[#D9EEF7] bg-white px-3 font-semibold text-[#0F2854] transition hover:border-[#4988C4] hover:bg-[#BDE8F5]/40 disabled:cursor-not-allowed disabled:opacity-50 dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-white dark:hover:bg-[#1C4D8D]/50"
        >
          Previous
        </button>
        <button
          type="button"
          disabled={!hasNext || busy}
          onClick={onNext}
          className="inline-flex h-9 items-center justify-center rounded-md bg-[#0F2854] px-3 font-semibold text-white transition hover:bg-[#1C4D8D] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-[#4988C4] dark:hover:bg-[#1C4D8D]"
        >
          Next
        </button>
      </div>
    </div>
  );
}
