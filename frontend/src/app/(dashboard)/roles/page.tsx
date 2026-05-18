import { redirect } from "next/navigation";

import { canAccessFeature } from "@/lib/api/featureAccess";
import { fetchPaginated } from "@/lib/api/pagination";
import { getAuthSession } from "@/lib/auth/session";
import { getLimitParam, getPageParam, getStringParam } from "@/lib/navigation/searchParams";
import { AccessDenied, PageContent, PageHeader } from "@/shared/components/PageHeader";
import {
  ResourcePageContent,
  type ResourceItem,
  type ResourcePermissionItem,
} from "@/shared/components/ResourcePage";

import {
  assignRolePermissionsAction,
  createRoleAction,
  deleteRoleAction,
  updateRoleAction,
} from "./_actions/mutate-role";

type RolesPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function RolesPage({ searchParams }: RolesPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const resolvedSearchParams = await searchParams;
  const page = getPageParam(resolvedSearchParams.page);
  const limit = getLimitParam(resolvedSearchParams.limit);
  const search = getStringParam(resolvedSearchParams.search);

  const [
    canViewRoles,
    canManageRoles,
    canDeleteRoles,
    canViewPermissions,
  ] = await Promise.all([
    canAccessFeature(session.accessToken, "role/view"),
    canAccessFeature(session.accessToken, "role/manage"),
    canAccessFeature(session.accessToken, "role/delete"),
    canAccessFeature(session.accessToken, "permission/view"),
  ]);

  if (!canViewRoles) {
    return <AccessDenied message="Your account does not have access to view roles." />;
  }

  const [roles, permissions] = await Promise.all([
    fetchPaginated<ResourceItem>({
      accessToken: session.accessToken,
      path: "/roles",
      page,
      limit,
      search,
    }),
    canViewPermissions
      ? fetchPaginated<ResourcePermissionItem>({
          accessToken: session.accessToken,
          path: "/permissions",
          page: 0,
          limit: 200,
          search: "",
        })
      : { data: [], meta: { page: 0, limit: 200, total: 0 } },
  ]);

  return (
    <PageContent>
      <PageHeader title="Roles" subtitle="View and manage user roles." />

      <ResourcePageContent
        key={`${roles.meta.page}:${roles.meta.limit}:${roles.meta.total}:${search}`}
        items={roles.data}
        meta={roles.meta}
        search={search}
        resourceLabel="Role"
        resourceLabelPlural="roles"
        emptyMessage="No roles found."
        canCreate={canManageRoles}
        canManage={canManageRoles}
        canDelete={canDeleteRoles}
        canAssignPermissions={canManageRoles && canViewPermissions}
        showDefault
        showPermissions
        allPermissions={permissions.data}
        createAction={createRoleAction}
        updateAction={updateRoleAction}
        deleteAction={deleteRoleAction}
        assignPermissionsAction={assignRolePermissionsAction}
      />
    </PageContent>
  );
}
