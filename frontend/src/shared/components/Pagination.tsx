"use client";

import { useState } from "react";

type PaginationProps = {
  page: number;
  limit: number;
  total: number;
  itemLabel: string;
  busy?: boolean;
  onPageChange: (page: number) => void;
};

export function Pagination({
  page,
  limit,
  total,
  itemLabel,
  busy = false,
  onPageChange,
}: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const currentPage = Math.min(page + 1, totalPages);
  const [pageInput, setPageInput] = useState(String(currentPage));

  return (
    <div
      className="flex border-t border-[#D9EEF7] px-4 py-3 text-sm text-[#1C4D8D] dark:border-[#1C4D8D] dark:text-[#BDE8F5]"
      aria-busy={busy}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span>Page</span>
        <label className="sr-only" htmlFor="pagination-page">
          Page number
        </label>
        <input
          id="pagination-page"
          type="number"
          min={1}
          max={totalPages}
          inputMode="numeric"
          value={pageInput}
          onChange={(event) => {
            setPageInput(getGuardedPageInput(event.currentTarget.value, totalPages));
          }}
          onBlur={() => onPageChange(getCommittedPage(pageInput, totalPages))}
          onKeyDown={(event) => {
            if (event.key !== "Enter") {
              return;
            }

            event.currentTarget.blur();
          }}
          className="h-9 w-16 rounded-md border border-[#D9EEF7] bg-white px-2 text-center font-semibold text-[#0F2854] outline-none transition focus:border-[#4988C4] focus:ring-2 focus:ring-[#BDE8F5] dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-white"
        />
        <span>
          of <span className="font-semibold">{totalPages}</span>
        </span>
        <span className="text-[#4988C4]">
          ({total} {itemLabel})
        </span>
      </div>
    </div>
  );
}

function getGuardedPageInput(value: string, totalPages: number) {
  if (value === "") {
    return "";
  }

  const page = Number.parseInt(value, 10);

  if (!Number.isFinite(page)) {
    return "";
  }

  return String(Math.min(Math.max(page, 1), totalPages));
}

function getCommittedPage(value: string, totalPages: number) {
  const page = Number.parseInt(value, 10);

  if (!Number.isFinite(page)) {
    return 1;
  }

  return Math.min(Math.max(page, 1), totalPages);
}
