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
  getCursorListKey,
  parseCursorListState,
  type PageSearchParams,
} from "../_lib/cursor-list-state";

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

  const state = parseCursorListState(await searchParams);
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
        key={getCursorListKey(state)}
        canDeletePermissions={data.canDeletePermissions}
        canManagePermissions={data.canManagePermissions}
        meta={data.permissions.meta}
        permissions={data.permissions.data}
        state={state}
      />
    </PageContent>
  );
}
