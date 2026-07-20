import type { StaticImageData } from "next/image";
import type { ReactNode } from "react";

import firmwareIcon from "../_assets/FirmwareIcon.svg";
import networkIcon from "../_assets/NetworkIcon.svg";
import nodeIcon from "../_assets/NodeIcon.svg";
import permissionIcon from "../_assets/PermissionIcon.svg";
import rangingIcon from "../_assets/RangingIcon.svg";
import roleIcon from "../_assets/RoleIcon.svg";
import settingsIcon from "../_assets/SettingsIcon.svg";
import userIcon from "../_assets/UserIcon.svg";
import { SidebarClient } from "./SidebarClient";

export type SidebarConfigMenu = {
  label: string;
  href: string;
  permissionNames?: string[];
  icon: StaticImageData;
};

export type SidebarConfigGroup = {
  label: string;
  menus: SidebarConfigMenu[];
};

export const sidebarConfig = [
  {
    label: "Node",
    menus: [
      {
        label: "Nodes",
        href: "/node/nodes",
        permissionNames: ["node/view"],
        icon: nodeIcon,
      },
      {
        label: "Networks",
        href: "/node/network",
        permissionNames: ["node-network/view"],
        icon: networkIcon,
      },
      {
        label: "Range Monitor",
        href: "/node/range-monitor",
        permissionNames: ["node/view", "ranging/view"],
        icon: rangingIcon,
      },
    ],
  },
  {
    label: "Admin",
    menus: [
      {
        label: "Users",
        href: "/admin/users",
        permissionNames: ["user/view"],
        icon: userIcon,
      },
      {
        label: "Roles",
        href: "/admin/roles",
        permissionNames: ["role/view"],
        icon: roleIcon,
      },
      {
        label: "Permissions",
        href: "/admin/permissions",
        permissionNames: ["permission/view"],
        icon: permissionIcon,
      },
      {
        label: "Firmware",
        href: "/admin/firmware",
        permissionNames: ["firmware/view"],
        icon: firmwareIcon,
      },
      {
        label: "Settings",
        href: "/admin/settings",
        permissionNames: ["ranging-scheduler-config/view"],
        icon: settingsIcon,
      },
    ],
  },
] satisfies SidebarConfigGroup[];

type SidebarProps = {
  userName: string;
  groups: SidebarConfigGroup[];
  signOutAction: () => Promise<void>;
  signOutButton: ReactNode;
};

export function Sidebar({
  userName,
  groups,
  signOutAction,
  signOutButton,
}: SidebarProps) {
  return (
    <SidebarClient
      userName={userName}
      groups={groups}
      signOutAction={signOutAction}
      signOutButton={signOutButton}
    />
  );
}
