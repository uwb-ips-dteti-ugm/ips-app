import { getFirmwares, type FirmwareResponse } from "@/lib/api/firmware";
import { getNodes } from "@/lib/api/node";
import { getMyPermissions } from "@/lib/api/user";

export type FirmwarePageData = {
  canDeleteFirmware: boolean;
  canManageFirmware: boolean;
  canViewFirmware: boolean;
  connectedNodeCount: number;
  firmwares: FirmwareResponse[];
};

export async function getFirmwarePageData(accessToken: string): Promise<FirmwarePageData> {
  const permissionNames = await readPermissionNames(accessToken);
  const canDeleteFirmware = permissionNames.has("firmware/delete");
  const canManageFirmware = permissionNames.has("firmware/manage");
  const canViewFirmware = permissionNames.has("firmware/view");

  if (!canViewFirmware) {
    return {
      canDeleteFirmware,
      canManageFirmware,
      canViewFirmware,
      connectedNodeCount: 0,
      firmwares: [],
    };
  }

  const [firmwaresPage, connectedNodes] = await Promise.all([
    getFirmwares({ limit: 100 }, { accessToken }),
    getNodes({ is_online: true, limit: 1 }, { accessToken }),
  ]);

  return {
    canDeleteFirmware,
    canManageFirmware,
    canViewFirmware,
    connectedNodeCount: connectedNodes.total,
    firmwares: firmwaresPage.items,
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
