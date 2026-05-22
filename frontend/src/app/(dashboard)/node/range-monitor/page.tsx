import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import { RangeMonitorContent } from "./_components/RangeMonitorContent";
import { getRangeMonitorPageData } from "./_lib/get-range-monitor-page-data";

export default async function RangeMonitorPage() {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const data = await getRangeMonitorPageData(session.accessToken);

  if (!data.canViewRangeMonitor) {
    return (
      <AccessDenied message="Your account does not have access to view range monitoring." />
    );
  }

  return (
    <PageContent>
      <PageHeader
        title="Range Monitor"
        subtitle="Select a node to view live ranges within its UWB network."
      />

      <RangeMonitorContent nodes={data.nodes} />
    </PageContent>
  );
}
