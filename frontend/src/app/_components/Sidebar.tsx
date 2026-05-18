import { type StaticImageData } from "next/image";
import { type ReactNode } from "react";

import featureIcon from "../_assets/FeatureIcon.svg";
import nodeIcon from "../_assets/NodeIcon.svg";
import permissionIcon from "../_assets/PermissionIcon.svg";
import rangingIcon from "../_assets/RangingIcon.svg";
import roleIcon from "../_assets/RoleIcon.svg";
import userIcon from "../_assets/UserIcon.svg";
import { SidebarClient } from "./SidebarClient";

export type SidebarConfigMenu = {
  label: string;
  href: string;
  featureName?: string;
  featureNames?: string[];
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
        label: "List",
        href: "/node/list",
        featureName: "node/view",
        icon: nodeIcon,
      },
      {
        label: "Ranging",
        href: "/node/ranging",
        featureNames: ["node/view", "record/view"],
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
        featureName: "user/view",
        icon: userIcon,
      },
      {
        label: "Roles",
        href: "/admin/roles",
        featureName: "role/view",
        icon: roleIcon,
      },
      {
        label: "Permissions",
        href: "/admin/permissions",
        featureName: "permission/view",
        icon: permissionIcon,
      },
      {
        label: "Features",
        href: "/admin/features",
        featureName: "feature/view",
        icon: featureIcon,
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
