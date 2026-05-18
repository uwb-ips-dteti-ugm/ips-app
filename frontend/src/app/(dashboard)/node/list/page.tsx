import { redirect } from "next/navigation";

import { canAccessFeature } from "@/lib/api/featureAccess";
import {
  fetchNodes,
  fetchRegisteredNodeIds,
} from "@/lib/api/nodes";
import { getAuthSession } from "@/lib/auth/session";
import { AccessDenied, PageContent, PageHeader } from "@/shared/components/PageHeader";

import { NodeSection } from "./_components/NodeSection";

export default async function NodeListPage() {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const [canViewNodes, canManageNodes, canDeleteNodes] = await Promise.all([
    canAccessFeature(session.accessToken, "node/view"),
    canAccessFeature(session.accessToken, "node/manage"),
    canAccessFeature(session.accessToken, "node/delete"),
  ]);

  if (!canViewNodes) {
    return <AccessDenied message="Your account does not have access to view nodes." />;
  }

  const [waitingNodes, approvedNodes, registeredNodeIds] = await Promise.all([
    fetchNodes({
      accessToken: session.accessToken,
      status: "pending",
      limit: 100,
    }),
    fetchNodes({
      accessToken: session.accessToken,
      status: "approved",
      limit: 100,
    }),
    fetchRegisteredNodeIds(session.accessToken),
  ]);
  const registeredNodeIdSet = new Set(registeredNodeIds);

  return (
    <PageContent>
      <PageHeader
        title="Nodes"
        subtitle="Approve node registrations and monitor approved devices."
      />

      <NodeSection
        title="Waiting for Approval"
        subtitle="Nodes appear here after their first websocket connection attempt."
        emptyMessage="No nodes are waiting for approval."
        nodes={waitingNodes.data}
        registeredNodeIds={registeredNodeIdSet}
        canManage={canManageNodes}
        canDelete={canDeleteNodes}
        variant="waiting"
      />

      <NodeSection
        title="Approved Nodes"
        subtitle="Approved nodes can connect, receive commands, and report ranging records."
        emptyMessage="No approved nodes found."
        nodes={approvedNodes.data}
        registeredNodeIds={registeredNodeIdSet}
        canManage={canManageNodes}
        canDelete={canDeleteNodes}
        variant="approved"
      />
    </PageContent>
  );
}
