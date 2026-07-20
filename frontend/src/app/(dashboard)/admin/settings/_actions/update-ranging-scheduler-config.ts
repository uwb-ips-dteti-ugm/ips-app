"use server";

import { revalidatePath } from "next/cache";

import { isApiError } from "@/lib/api/client";
import {
  resetRangingSchedulerConfig,
  updateRangingSchedulerConfig,
  type UpdateRangingSchedulerConfigRequest,
} from "@/lib/api/ranging-scheduler-config";
import { getAuthSession } from "@/lib/auth/session";

const SETTINGS_PATH = "/admin/settings";

export type SettingsUpdateActionResult =
  | {
      ok: true;
    }
  | {
      error: string;
      ok: false;
    };

export async function updateRangingSchedulerConfigAction(
  request: UpdateRangingSchedulerConfigRequest,
): Promise<SettingsUpdateActionResult> {
  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before updating settings.",
      ok: false,
    };
  }

  try {
    await updateRangingSchedulerConfig(request, {
      accessToken: session.accessToken,
    });
    revalidatePath(SETTINGS_PATH);
    return { ok: true };
  } catch (error) {
    return updateErrorResult(error, "The ranging scheduler settings could not be updated.");
  }
}

export async function resetRangingSchedulerConfigAction(): Promise<SettingsUpdateActionResult> {
  const session = await getAuthSession();
  if (!session) {
    return {
      error: "Your session has expired. Sign in again before updating settings.",
      ok: false,
    };
  }

  try {
    await resetRangingSchedulerConfig({ accessToken: session.accessToken });
    revalidatePath(SETTINGS_PATH);
    return { ok: true };
  } catch (error) {
    return updateErrorResult(error, "The ranging scheduler settings could not be reset.");
  }
}

function updateErrorResult(
  error: unknown,
  fallback: string,
): SettingsUpdateActionResult {
  return {
    error: isApiError(error) ? error.message : fallback,
    ok: false,
  };
}
