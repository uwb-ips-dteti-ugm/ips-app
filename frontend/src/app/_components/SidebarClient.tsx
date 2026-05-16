"use client";

import Image from "next/image";
import { useState, type ReactNode } from "react";

import chevronDownIcon from "@/shared/assets/ChevronDownIcon.svg";

import exitIcon from "../_assets/ExitIcon.svg";
import hamburgerIcon from "../_assets/HamburgerIcon.svg";
import type { SidebarConfigGroup, SidebarConfigMenu } from "./Sidebar";

type SidebarClientProps = {
  userName: string;
  groups: SidebarConfigGroup[];
  signOutAction: () => Promise<void>;
  signOutButton: ReactNode;
};

export function SidebarClient({
  userName,
  groups,
  signOutAction,
  signOutButton,
}: SidebarClientProps) {
  const [isOpen, setIsOpen] = useState(false);
  const firstName = getFirstName(userName);

  return (
    <aside
      className={`sticky top-0 flex h-dvh shrink-0 flex-col overflow-hidden border-r border-[#D9EEF7] bg-white py-5 text-[#0F2854] transition-[width,padding] duration-200 dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-white ${
        isOpen ? "w-72 px-4" : "w-18 px-3"
      }`}
    >
      <div
        className={`mb-8 flex items-center ${
          isOpen ? "justify-between gap-2" : "justify-center"
        }`}
      >
        {isOpen && (
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <Image
              className="shrink-0 dark:hidden"
              src="/app-logo-dark.svg"
              alt="IPS App"
              width={36}
              height={36}
              priority
            />
            <Image
              className="hidden shrink-0 dark:block"
              src="/app-logo-light.svg"
              alt="IPS App"
              width={36}
              height={36}
              priority
            />
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold leading-5">
                Indoor Positioning System
              </div>
              <div className="truncate text-xs text-[#1C4D8D] dark:text-[#BDE8F5]">
                Hello, {firstName}!
              </div>
            </div>
          </div>
        )}
        <button
          type="button"
          aria-label={isOpen ? "Collapse sidebar" : "Expand sidebar"}
          aria-expanded={isOpen}
          onClick={() => setIsOpen((current) => !current)}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-transparent transition hover:bg-[#BDE8F5]/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] dark:hover:bg-[#1C4D8D]/50"
        >
          <Image
            src={hamburgerIcon}
            alt=""
            width={22}
            height={22}
            className="h-5.5 w-5.5 shrink-0 dark:brightness-0 dark:invert"
          />
        </button>
      </div>

      {isOpen ? (
        <>
          <nav className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto">
            {groups.map((group) => (
              <SidebarGroup key={group.label} group={group} />
            ))}
          </nav>

          <form action={signOutAction} className="shrink-0 px-2 pt-4">
            {signOutButton}
          </form>
        </>
      ) : (
        <>
          <nav className="flex min-h-0 flex-1 flex-col items-center gap-2 overflow-y-auto">
            {groups.flatMap((group) =>
              group.menus.map((menu) => (
                <SidebarCollapsedItem key={menu.href} menu={menu} />
              )),
            )}
          </nav>

          <form action={signOutAction} className="flex shrink-0 justify-center pt-4">
            <SidebarCollapsedSignOutButton />
          </form>
        </>
      )}
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

function SidebarCollapsedItem({ menu }: { menu: SidebarConfigMenu }) {
  return (
    <a
      href={menu.href}
      aria-label={menu.label}
      title={menu.label}
      className="flex h-10 w-10 items-center justify-center rounded-md text-[#0F2854] transition hover:bg-[#BDE8F5]/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] dark:text-white dark:hover:bg-[#1C4D8D]"
    >
      <Image
        src={menu.icon}
        alt=""
        width={20}
        height={20}
        className="shrink-0 dark:brightness-0 dark:invert"
      />
    </a>
  );
}

function SidebarCollapsedSignOutButton() {
  return (
    <button
      type="submit"
      aria-label="Sign out"
      title="Sign out"
      className="group flex h-10 w-10 items-center justify-center rounded-md border border-[#E05A5A] bg-transparent text-[#E05A5A] transition hover:bg-[#E05A5A] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#E05A5A]"
    >
      <Image
        src={exitIcon}
        alt=""
        width={18}
        height={18}
        className="h-4.5 w-4.5 shrink-0 transition group-hover:brightness-0 group-hover:invert"
      />
    </button>
  );
}

function getFirstName(name: string): string {
  return name.trim().split(/\s+/)[0] || "there";
}
