import { redirect } from "next/navigation";

import { DashboardShell } from "@/app/_components/DashboardShell";
import { canAccessFeature } from "@/lib/api/featureAccess";
import { fetchPaginated } from "@/lib/api/pagination";
import { getAuthSession } from "@/lib/auth/session";
import { getLimitParam, getPageParam, getStringParam } from "@/lib/navigation/searchParams";
import { AccessDenied, PageContent, PageHeader } from "@/shared/components/PageHeader";
import {
  ResourcePageContent,
  type ResourcePermissionItem,
} from "@/shared/components/ResourcePage";

import {
  createPermissionAction,
  deletePermissionAction,
  updatePermissionAction,
} from "./_actions/mutate-permission";

type PermissionsPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function PermissionsPage({
  searchParams,
}: PermissionsPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const resolvedSearchParams = await searchParams;
  const page = getPageParam(resolvedSearchParams.page);
  const limit = getLimitParam(resolvedSearchParams.limit);
  const search = getStringParam(resolvedSearchParams.search);

  const [canViewPermissions, canManagePermissions, canDeletePermissions] =
    await Promise.all([
      canAccessFeature(session.accessToken, "permission/view"),
      canAccessFeature(session.accessToken, "permission/manage"),
      canAccessFeature(session.accessToken, "permission/delete"),
    ]);

  if (!canViewPermissions) {
    return (
      <DashboardShell session={session}>
        <AccessDenied message="Your account does not have access to view permissions." />
      </DashboardShell>
    );
  }

  const permissions = await fetchPaginated<ResourcePermissionItem>({
    accessToken: session.accessToken,
    path: "/permissions",
    page,
    limit,
    search,
  });

  return (
    <DashboardShell session={session}>
      <PageContent>
        <PageHeader
          title="Permissions"
          subtitle="View and manage permission resources."
        />

        <ResourcePageContent
          key={`${permissions.meta.page}:${permissions.meta.limit}:${permissions.meta.total}:${search}`}
          items={permissions.data}
          meta={permissions.meta}
          search={search}
          resourceLabel="Permission"
          resourceLabelPlural="permissions"
          emptyMessage="No permissions found."
          canCreate={canManagePermissions}
          canManage={canManagePermissions}
          canDelete={canDeletePermissions}
          createAction={createPermissionAction}
          updateAction={updatePermissionAction}
          deleteAction={deletePermissionAction}
        />
      </PageContent>
    </DashboardShell>
  );
}
