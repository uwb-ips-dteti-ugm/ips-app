import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";

import { DashboardShell } from "./_components/DashboardShell";

export default async function Home() {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  return (
    <DashboardShell session={session}>
      <div />
    </DashboardShell>
  );
}
