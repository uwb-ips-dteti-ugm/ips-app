import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import { NodesListContent } from "./_components/NodesListContent";
import { getNodesPageData } from "./_lib/get-nodes-page-data";
import {
  getNodesListKey,
  parseNodesListState,
  type NodesPageSearchParams,
} from "./_lib/nodes-list-state";

type NodesPageProps = {
  searchParams: Promise<NodesPageSearchParams>;
};

export default async function NodesPage({ searchParams }: NodesPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const state = parseNodesListState(await searchParams);
  const data = await getNodesPageData(session.accessToken, state);

  if (!data.canViewNodes) {
    return <AccessDenied message="Your account does not have access to view nodes." />;
  }

  return (
    <PageContent>
      <PageHeader title="Nodes" subtitle="View registered UWB nodes." />

      <NodesListContent
        canManageNodes={data.canManageNodes}
        key={getNodesListKey(state)}
        limit={data.nodes.limit}
        networks={data.networks}
        nodes={data.nodes.items}
        state={state}
        total={data.nodes.total}
      />
    </PageContent>
  );
}
