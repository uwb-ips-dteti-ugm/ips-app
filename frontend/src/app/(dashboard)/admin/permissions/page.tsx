import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import { PermissionsListContent } from "./_components/PermissionsListContent";
import { getPermissionsPageData } from "./_lib/get-permissions-page-data";
import {
  getPageListKey,
  parsePageListState,
  type PageSearchParams,
} from "../_lib/page-list-state";

type PermissionsPageProps = {
  searchParams: Promise<PageSearchParams>;
};

export default async function PermissionsPage({
  searchParams,
}: PermissionsPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const state = parsePageListState(await searchParams);
  const data = await getPermissionsPageData(session.accessToken, state);

  if (!data.canViewPermissions) {
    return (
      <AccessDenied message="Your account does not have access to view permissions." />
    );
  }

  return (
    <PageContent>
      <PageHeader
        title="Permissions"
        subtitle="View and manage permission resources."
      />

      <PermissionsListContent
        key={getPageListKey(state)}
        canDeletePermissions={data.canDeletePermissions}
        canManagePermissions={data.canManagePermissions}
        limit={data.permissions.limit}
        permissions={data.permissions.items}
        state={state}
        total={data.permissions.total}
      />
    </PageContent>
  );
}
