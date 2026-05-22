import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import { RolesListContent } from "./_components/RolesListContent";
import { getRolesPageData } from "./_lib/get-roles-page-data";
import {
  getCursorListKey,
  parseCursorListState,
  type PageSearchParams,
} from "../_lib/cursor-list-state";

type RolesPageProps = {
  searchParams: Promise<PageSearchParams>;
};

export default async function RolesPage({ searchParams }: RolesPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const state = parseCursorListState(await searchParams);
  const data = await getRolesPageData(session.accessToken, state);

  if (!data.canViewRoles) {
    return (
      <AccessDenied message="Your account does not have access to view roles." />
    );
  }

  return (
    <PageContent>
      <PageHeader title="Roles" subtitle="View and manage user roles." />

      <RolesListContent
        key={getCursorListKey(state)}
        canDeleteRoles={data.canDeleteRoles}
        canManageRoles={data.canManageRoles}
        canViewPermissions={data.canViewPermissions}
        meta={data.roles.meta}
        permissions={data.permissions}
        roles={data.roles.data}
        state={state}
      />
    </PageContent>
  );
}
