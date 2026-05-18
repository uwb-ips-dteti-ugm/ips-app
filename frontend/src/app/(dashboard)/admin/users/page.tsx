import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import { UsersPageContent } from "./_components/UsersPageContent";
import {
  getUsersPageData,
  type UsersPageSearchParams,
} from "./_lib/get-users-page-data";

export default async function UsersPage({
  searchParams,
}: {
  searchParams: Promise<UsersPageSearchParams>;
}) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const data = await getUsersPageData(session.accessToken, await searchParams);

  if (!data.canViewUsers) {
    return <AccessDenied message="Your account does not have access to view users." />;
  }

  return (
    <PageContent>
      <PageHeader title="Users" subtitle="View and manage users." />

      <UsersPageContent
        key={`${data.users.meta.page}:${data.users.meta.limit}:${data.users.meta.total}:${data.filters.search}:${data.filters.roleId}:${data.filters.state}:${data.filters.status}`}
        users={data.users.data}
        meta={data.users.meta}
        filters={data.filters}
        roles={data.roles}
        canRegisterUsers={data.canRegisterUsers}
        canManageUsers={data.canManageUsers}
        canDeleteUsers={data.canDeleteUsers}
      />
    </PageContent>
  );
}
