import { type ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
};

export function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  return (
    <header className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h1 className="text-2xl font-semibold text-[#0F2854] dark:text-white">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-1 text-sm text-[#4988C4] dark:text-[#BDE8F5]">
            {subtitle}
          </p>
        )}
      </div>
      {actions}
    </header>
  );
}

export function PageContent({ children }: { children: ReactNode }) {
  return <div className="flex min-h-dvh flex-col gap-5 p-6">{children}</div>;
}

export function AccessDenied({
  title = "Access denied",
  message,
}: {
  title?: string;
  message: string;
}) {
  return (
    <div className="flex min-h-dvh items-center justify-center p-6">
      <div className="max-w-md text-center">
        <h1 className="text-xl font-semibold text-[#0F2854] dark:text-white">
          {title}
        </h1>
        <p className="mt-2 text-sm text-[#4988C4] dark:text-[#BDE8F5]">
          {message}
        </p>
      </div>
    </div>
  );
}
