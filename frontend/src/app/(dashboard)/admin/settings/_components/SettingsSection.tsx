import type { ReactNode } from "react";

type SettingsSectionProps = {
  children: ReactNode;
  description?: string;
  title: string;
};

export function SettingsSection({
  children,
  description,
  title,
}: SettingsSectionProps) {
  return (
    <section className="rounded-md border border-[#D9EEF7] bg-white p-5 dark:border-[#1C4D8D] dark:bg-[#07111F]">
      <header className="mb-4">
        <h2 className="text-base font-semibold text-[#0F2854] dark:text-white">
          {title}
        </h2>
        {description ? (
          <p className="mt-1 text-sm text-[#4988C4] dark:text-[#BDE8F5]">
            {description}
          </p>
        ) : null}
      </header>
      {children}
    </section>
  );
}
