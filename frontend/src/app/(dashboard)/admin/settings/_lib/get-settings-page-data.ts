import {
  getRangingSchedulerConfig,
  type RangingSchedulerConfigResponse,
} from "@/lib/api/ranging-scheduler-config";
import { getMyPermissions } from "@/lib/api/user";

export type SettingsPageData = {
  canManageRangingSchedulerConfig: boolean;
  canViewRangingSchedulerConfig: boolean;
  rangingSchedulerConfig: RangingSchedulerConfigResponse | null;
};

export async function getSettingsPageData(
  accessToken: string,
): Promise<SettingsPageData> {
  const permissionNames = await readPermissionNames(accessToken);
  const canManageRangingSchedulerConfig = permissionNames.has(
    "ranging-scheduler-config/manage",
  );
  const canViewRangingSchedulerConfig = permissionNames.has(
    "ranging-scheduler-config/view",
  );

  if (!canViewRangingSchedulerConfig) {
    return {
      canManageRangingSchedulerConfig,
      canViewRangingSchedulerConfig,
      rangingSchedulerConfig: null,
    };
  }

  const rangingSchedulerConfig = await getRangingSchedulerConfig({
    accessToken,
  });

  return {
    canManageRangingSchedulerConfig,
    canViewRangingSchedulerConfig,
    rangingSchedulerConfig,
  };
}

async function readPermissionNames(accessToken: string): Promise<Set<string>> {
  try {
    const permissions = await getMyPermissions({ accessToken });
    return new Set(permissions.map((permission) => permission.name));
  } catch {
    return new Set();
  }
}
