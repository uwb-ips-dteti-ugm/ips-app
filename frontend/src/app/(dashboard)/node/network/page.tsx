import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import {
  getCursorListKey,
  parseCursorListState,
  type PageSearchParams,
} from "../../admin/_lib/cursor-list-state";
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

  const state = parseCursorListState(await searchParams);
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
        key={getCursorListKey(state)}
        canDeleteNodeNetworks={data.canDeleteNodeNetworks}
        canManageNodeNetworks={data.canManageNodeNetworks}
        meta={data.nodeNetworks.meta}
        nodeNetworks={data.nodeNetworks.data}
        state={state}
      />
    </PageContent>
  );
}
