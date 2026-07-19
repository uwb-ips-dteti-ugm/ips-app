import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import {
  getPageListKey,
  parsePageListState,
  type PageSearchParams,
} from "../../admin/_lib/page-list-state";
import { NodeNetworksListContent } from "./_components/NodeNetworksListContent";
import { getNodeNetworksPageData } from "./_lib/get-node-networks-page-data";

type NodeNetworksPageProps = {
  searchParams: Promise<PageSearchParams>;
};

export default async function NodeNetworksPage({
  searchParams,
}: NodeNetworksPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const state = parsePageListState(await searchParams);
  const data = await getNodeNetworksPageData(session.accessToken, state);

  if (!data.canViewNodeNetworks) {
    return (
      <AccessDenied message="Your account does not have access to view node networks." />
    );
  }

  return (
    <PageContent>
      <PageHeader
        title="Node Networks"
        subtitle="View and manage UWB node networks."
      />

      <NodeNetworksListContent
        key={getPageListKey(state)}
        canDeleteNodeNetworks={data.canDeleteNodeNetworks}
        canManageNodeNetworks={data.canManageNodeNetworks}
        limit={data.nodeNetworks.limit}
        nodeNetworks={data.nodeNetworks.items}
        state={state}
        total={data.nodeNetworks.total}
      />
    </PageContent>
  );
}
