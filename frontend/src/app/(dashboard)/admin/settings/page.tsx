import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import { RangingSchedulerConfigForm } from "./_components/RangingSchedulerConfigForm";
import { SettingsSection } from "./_components/SettingsSection";
import { getSettingsPageData } from "./_lib/get-settings-page-data";

export default async function SettingsPage() {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const data = await getSettingsPageData(session.accessToken);

  if (!data.canViewRangingSchedulerConfig || !data.rangingSchedulerConfig) {
    return (
      <AccessDenied message="Your account does not have access to view settings." />
    );
  }

  return (
    <PageContent>
      <PageHeader
        title="Settings"
        subtitle="Manage application configuration."
      />

      <div className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto">
        <SettingsSection
          title="Ranging Scheduler"
          description="Timing parameters for the UWB ranging task scheduler."
        >
          <RangingSchedulerConfigForm
            canManage={data.canManageRangingSchedulerConfig}
            config={data.rangingSchedulerConfig}
          />
        </SettingsSection>
      </div>
    </PageContent>
  );
}
