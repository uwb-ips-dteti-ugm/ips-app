import type { ReactNode } from "react";

export function DescriptionList({ children }: { children: ReactNode }) {
  return <dl className="flex flex-col gap-3">{children}</dl>;
}

export function DescriptionRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="grid gap-1 border-b border-[#D9EEF7] pb-3 last:border-b-0 last:pb-0 dark:border-[#1C4D8D]">
      <dt className="text-xs font-semibold uppercase text-[#4988C4] dark:text-[#BDE8F5]">
        {label}
      </dt>
      <dd className="break-words text-sm text-[#0F2854] dark:text-white">
        {value}
      </dd>
    </div>
  );
}
