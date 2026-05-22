import { redirect } from "next/navigation";

import { DashboardShell } from "@/app/_components/DashboardShell";
import { getAuthSession } from "@/lib/auth/session";

export default async function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  return <DashboardShell session={session}>{children}</DashboardShell>;
}
