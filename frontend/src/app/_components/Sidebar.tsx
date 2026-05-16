import Image, { type StaticImageData } from "next/image";

import chevronDownIcon from "../_assets/ChevronDownIcon.svg";
import roleIcon from "../_assets/RoleIcon.svg";
import userIcon from "../_assets/UserIcon.svg";

export type SidebarConfigMenu = {
  label: string;
  href: string;
  featureName: string;
  icon: StaticImageData;
};

export type SidebarConfigGroup = {
  label: string;
  menus: SidebarConfigMenu[];
};

export const sidebarConfig = [
  {
    label: "Admin",
    menus: [
      {
        label: "User",
        href: "/users",
        featureName: "user/view",
        icon: userIcon,
      },
      {
        label: "Role",
        href: "/roles",
        featureName: "role/view",
        icon: roleIcon,
      },
    ],
  },
] satisfies SidebarConfigGroup[];

type SidebarProps = {
  userName: string;
  groups: SidebarConfigGroup[];
  signOutAction: () => Promise<void>;
  signOutButton: React.ReactNode;
};

export function Sidebar({
  userName,
  groups,
  signOutAction,
  signOutButton,
}: SidebarProps) {
  const firstName = getFirstName(userName);

  return (
    <aside className="flex min-h-dvh w-72 flex-col border-r border-[#D9EEF7] bg-white px-4 py-5 text-[#0F2854] dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-white">
      <div className="mb-8 flex items-center gap-3 px-2">
        <Image
          className="dark:hidden"
          src="/app-logo-dark.svg"
          alt="IPS App"
          width={36}
          height={36}
          priority
        />
        <Image
          className="hidden dark:block"
          src="/app-logo-light.svg"
          alt="IPS App"
          width={36}
          height={36}
          priority
        />
        <div>
          <div className="text-sm font-semibold leading-5">
            Indoor Positioning System
          </div>
          <div className="text-xs text-[#1C4D8D] dark:text-[#BDE8F5]">
            Hello, {firstName}!
          </div>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-5">
        {groups.map((group) => (
          <SidebarGroup key={group.label} group={group} />
        ))}
      </nav>

      <form action={signOutAction} className="px-2 pt-4">
        {signOutButton}
      </form>
    </aside>
  );
}

function SidebarGroup({ group }: { group: SidebarConfigGroup }) {
  if (group.menus.length === 0) {
    return null;
  }

  return (
    <details className="group" open>
      <summary className="mb-2 flex cursor-pointer list-none items-center justify-between rounded-md px-3 py-1 text-xs font-semibold uppercase text-[#4988C4] outline-none transition hover:bg-[#BDE8F5]/40 focus-visible:ring-2 focus-visible:ring-[#4988C4] dark:text-[#BDE8F5] dark:hover:bg-[#1C4D8D]/50 [&::-webkit-details-marker]:hidden">
        {group.label}
        <Image
          src={chevronDownIcon}
          alt=""
          width={20}
          height={20}
          className="h-5 w-5 shrink-0 transition-transform group-open:rotate-180 dark:brightness-0 dark:invert"
        />
      </summary>
      <div className="flex flex-col gap-1">
        {group.menus.map((menu) => (
          <SidebarItem key={menu.href} menu={menu} />
        ))}
      </div>
    </details>
  );
}

function SidebarItem({ menu }: { menu: SidebarConfigMenu }) {
  return (
    <a
      href={menu.href}
      className="flex items-center gap-3 rounded-md px-3 py-2.5 text-base font-medium text-[#0F2854] transition hover:bg-[#BDE8F5]/50 dark:text-white dark:hover:bg-[#1C4D8D]"
    >
      <Image
        src={menu.icon}
        alt=""
        width={20}
        height={20}
        className="shrink-0 dark:brightness-0 dark:invert"
      />
      {menu.label}
    </a>
  );
}

function getFirstName(name: string): string {
  return name.trim().split(/\s+/)[0] || "there";
}
