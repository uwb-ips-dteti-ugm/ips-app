import type { ReactNode } from "react";

import { getMyPermissions } from "@/lib/api/user";
import type { AuthSession } from "@/lib/auth/session";

import { signOutAction } from "../_actions/sign-out";
import { Sidebar, sidebarConfig, type SidebarConfigMenu } from "./Sidebar";
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
  const grantedPermissions = await readGrantedPermissionNames(accessToken);

  return sidebarConfig
    .map((group) => ({
      ...group,
      menus: group.menus.filter((menu) =>
        getRequiredPermissionNames(menu).every((name) =>
          grantedPermissions.has(name),
        ),
      ),
    }))
    .filter((group) => group.menus.length > 0);
}

async function readGrantedPermissionNames(accessToken: string) {
  try {
    const permissions = await getMyPermissions({ accessToken });
    return new Set(permissions.map((permission) => permission.name));
  } catch {
    return new Set<string>();
  }
}

function getRequiredPermissionNames(menu: SidebarConfigMenu): string[] {
  return menu.permissionNames ?? [];
}
