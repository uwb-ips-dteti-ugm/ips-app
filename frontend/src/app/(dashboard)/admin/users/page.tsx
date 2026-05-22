import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import { UsersListContent } from "./_components/UsersListContent";
import { getUsersPageData } from "./_lib/get-users-page-data";
import {
  getUsersListKey,
  parseUsersListState,
  type UsersPageSearchParams,
} from "./_lib/users-list-state";

type UsersPageProps = {
  searchParams: Promise<UsersPageSearchParams>;
};

export default async function UsersPage({ searchParams }: UsersPageProps) {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const state = parseUsersListState(await searchParams);
  const data = await getUsersPageData(session.accessToken, state);

  if (!data.canViewUsers) {
    return (
      <AccessDenied message="Your account does not have access to view users." />
    );
  }

  return (
    <PageContent>
      <PageHeader title="Users" subtitle="View and manage user accounts." />

      <UsersListContent
        key={getUsersListKey(state)}
        canDeleteUsers={data.canDeleteUsers}
        canManageUsers={data.canManageUsers}
        canRegisterUsers={data.canRegisterUsers}
        meta={data.users.meta}
        roles={data.roles}
        state={state}
        users={data.users.data}
      />
    </PageContent>
  );
}
