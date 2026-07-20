"use server";

import { revalidatePath } from "next/cache";

import { isApiError } from "@/lib/api/client";
import { deleteFirmware } from "@/lib/api/firmware";
import { getAuthSession } from "@/lib/auth/session";

const FIRMWARE_PATH = "/admin/firmware";

export type DeleteFirmwareActionResult = { ok: true } | { error: string; ok: false };

export async function deleteFirmwareAction(
  firmwareId: string,
): Promise<DeleteFirmwareActionResult> {
  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before deleting firmware.",
      ok: false,
    };
  }

  try {
    await deleteFirmware(firmwareId, { accessToken: session.accessToken });
    revalidatePath(FIRMWARE_PATH);
    return { ok: true };
  } catch (error) {
    return {
      error: isApiError(error) ? error.message : "The firmware could not be deleted.",
      ok: false,
    };
  }
}
