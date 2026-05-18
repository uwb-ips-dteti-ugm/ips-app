import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import { AccessDenied, PageContent, PageHeader } from "@/shared/components/PageHeader";

import { RangingPairSelector } from "./_components/RangingPairSelector";
import { RangeResult } from "./_components/RangeResult";
import {
  getNodeRangingPageData,
  type NodeRangingPageSearchParams,
} from "./_lib/get-node-ranging-page-data";

export default async function NodeRangingPage({
  searchParams,
}: {
  searchParams: Promise<NodeRangingPageSearchParams>;
}) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const data = await getNodeRangingPageData(
    session.accessToken,
    await searchParams,
  );

  if (!data.canViewNodes || !data.canViewRecords) {
    return (
      <AccessDenied message="Your account does not have access to view node ranging data." />
    );
  }

  return (
    <PageContent>
      <PageHeader
        title="Node Ranging"
        subtitle="Select two approved nodes to inspect their latest recorded distance."
      />

      <RangingPairSelector
        sourceSearch={data.sourceSearch}
        targetSearch={data.targetSearch}
        sourceNodeDeviceId={data.sourceNodeDeviceId}
        targetNodeDeviceId={data.targetNodeDeviceId}
        sourceNodes={data.sourceNodes}
        targetNodes={data.targetNodes}
      />

      <RangeResult
        sourceNodeDeviceId={data.sourceNodeDeviceId}
        targetNodeDeviceId={data.targetNodeDeviceId}
        latestRecord={data.latestRecord}
      />
    </PageContent>
  );
}
