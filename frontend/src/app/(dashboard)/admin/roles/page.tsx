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
  getPageListKey,
  parsePageListState,
  type PageSearchParams,
} from "../_lib/page-list-state";

type RolesPageProps = {
  searchParams: Promise<PageSearchParams>;
};

export default async function RolesPage({ searchParams }: RolesPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const state = parsePageListState(await searchParams);
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
        key={getPageListKey(state)}
        canDeleteRoles={data.canDeleteRoles}
        canManageRoles={data.canManageRoles}
        canViewPermissions={data.canViewPermissions}
        limit={data.roles.limit}
        permissions={data.permissions}
        roles={data.roles.items}
        state={state}
        total={data.roles.total}
      />
    </PageContent>
  );
}
