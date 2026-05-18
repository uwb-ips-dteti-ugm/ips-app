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
  assignFeaturePermissionsAction,
  createFeatureAction,
  deleteFeatureAction,
  updateFeatureAction,
} from "./_actions/mutate-feature";

type FeaturesPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function FeaturesPage({ searchParams }: FeaturesPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const resolvedSearchParams = await searchParams;
  const page = getPageParam(resolvedSearchParams.page);
  const limit = getLimitParam(resolvedSearchParams.limit);
  const search = getStringParam(resolvedSearchParams.search);

  const [
    canViewFeatures,
    canManageFeatures,
    canDeleteFeatures,
    canViewPermissions,
  ] = await Promise.all([
    canAccessFeature(session.accessToken, "feature/view"),
    canAccessFeature(session.accessToken, "feature/manage"),
    canAccessFeature(session.accessToken, "feature/delete"),
    canAccessFeature(session.accessToken, "permission/view"),
  ]);

  if (!canViewFeatures) {
    return <AccessDenied message="Your account does not have access to view features." />;
  }

  const [features, permissions] = await Promise.all([
    fetchPaginated<ResourceItem>({
      accessToken: session.accessToken,
      path: "/features",
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
      <PageHeader
        title="Features"
        subtitle="View and manage feature gates."
      />

      <ResourcePageContent
        key={`${features.meta.page}:${features.meta.limit}:${features.meta.total}:${search}`}
        items={features.data}
        meta={features.meta}
        search={search}
        resourceLabel="Feature"
        resourceLabelPlural="features"
        emptyMessage="No features found."
        canCreate={canManageFeatures}
        canManage={canManageFeatures}
        canDelete={canDeleteFeatures}
        canAssignPermissions={canManageFeatures && canViewPermissions}
        showPermissions
        allPermissions={permissions.data}
        createAction={createFeatureAction}
        updateAction={updateFeatureAction}
        deleteAction={deleteFeatureAction}
        assignPermissionsAction={assignFeaturePermissionsAction}
      />
    </PageContent>
  );
}
