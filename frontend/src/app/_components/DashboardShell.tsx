import { type ReactNode } from "react";

import { canAccessFeature } from "@/lib/api/featureAccess";
import { type AuthSession } from "@/lib/auth/session";

import { signOutAction } from "../_actions/sign-out";
import { Sidebar, sidebarConfig } from "./Sidebar";
import { SignOutButton } from "./SignOutButton";

type DashboardShellProps = {
  session: AuthSession;
  children: ReactNode;
};

export async function DashboardShell({
  session,
  children,
}: DashboardShellProps) {
  const groups = await getAccessibleSidebarGroups(session.accessToken);

  return (
    <main className="flex min-h-dvh bg-[#F5FAFD] text-[#0F2854] dark:bg-black dark:text-white">
      <Sidebar
        userName={session.claims.name}
        groups={groups}
        signOutAction={signOutAction}
        signOutButton={<SignOutButton />}
      />
      <section className="min-w-0 flex-1">{children}</section>
    </main>
  );
}

async function getAccessibleSidebarGroups(accessToken: string) {
  const featureAccessEntries = await Promise.all(
    sidebarConfig.flatMap((group) =>
      group.menus.map(async (menu) => [
        menu.featureName,
        await canAccessFeature(accessToken, menu.featureName),
      ] as const),
    ),
  );
  const featureAccess = new Map(featureAccessEntries);

  return sidebarConfig
    .map((group) => ({
      ...group,
      menus: group.menus.filter((menu) => featureAccess.get(menu.featureName)),
    }))
    .filter((group) => group.menus.length > 0);
}
