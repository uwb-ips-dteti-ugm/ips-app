import { redirect } from "next/navigation";
import { type ReactNode } from "react";

import { DashboardShell } from "@/app/_components/DashboardShell";
import { getAuthSession } from "@/lib/auth/session";

export default async function DashboardLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  return <DashboardShell session={session}>{children}</DashboardShell>;
}
