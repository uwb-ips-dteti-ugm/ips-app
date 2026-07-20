"use server";

import { revalidatePath } from "next/cache";

import { isApiError } from "@/lib/api/client";
import { deployFirmware, type FirmwareDeployResponse } from "@/lib/api/firmware";
import { getAuthSession } from "@/lib/auth/session";

const FIRMWARE_PATH = "/admin/firmware";

export type DeployFirmwareActionResult =
  | {
      ok: true;
      result: FirmwareDeployResponse;
    }
  | {
      error: string;
      ok: false;
    };

export async function deployFirmwareAction(
  firmwareId: string,
): Promise<DeployFirmwareActionResult> {
  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before deploying firmware.",
      ok: false,
    };
  }

  try {
    const result = await deployFirmware(firmwareId, { accessToken: session.accessToken });
    revalidatePath(FIRMWARE_PATH);
    return { ok: true, result };
  } catch (error) {
    return {
      error: isApiError(error) ? error.message : "The firmware could not be deployed.",
      ok: false,
    };
  }
}
