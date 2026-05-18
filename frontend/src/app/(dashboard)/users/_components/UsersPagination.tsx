"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useTransition } from "react";

import { Pagination } from "@/shared/components/Pagination";

type UsersPaginationProps = {
  page: number;
  limit: number;
  total: number;
  search: string;
  roleId: string;
  state: string;
  status: string;
  onTableLoadingChange: (isLoading: boolean) => void;
};

export function UsersPagination({
  page,
  limit,
  total,
  search,
  roleId,
  state,
  status,
  onTableLoadingChange,
}: UsersPaginationProps) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  return (
    <Pagination
      page={page}
      limit={limit}
      total={total}
      itemLabel="users"
      busy={isPending}
      onPageChange={(nextPage) =>
        goToPage({
          page: nextPage,
          limit,
          search,
          roleId,
          state,
          status,
          onTableLoadingChange,
          pathname,
          router,
          searchParams,
          startTransition,
        })
      }
    />
  );
}

function goToPage({
  page,
  limit,
  search,
  roleId,
  state,
  status,
  onTableLoadingChange,
  pathname,
  router,
  searchParams,
  startTransition,
}: {
  page: number;
  limit: number;
  search: string;
  roleId: string;
  state: string;
  status: string;
  onTableLoadingChange: (isLoading: boolean) => void;
  pathname: string;
  router: ReturnType<typeof useRouter>;
  searchParams: ReturnType<typeof useSearchParams>;
  startTransition: (callback: () => void) => void;
}) {
  const guardedPage = Math.max(1, page);
  const nextSearchParams = new URLSearchParams(searchParams.toString());
  nextSearchParams.set("page", String(guardedPage - 1));
  nextSearchParams.set("limit", String(limit));

  if (search) {
    nextSearchParams.set("search", search);
  } else {
    nextSearchParams.delete("search");
  }

  if (roleId) {
    nextSearchParams.set("role_id", roleId);
  } else {
    nextSearchParams.delete("role_id");
  }

  if (state) {
    nextSearchParams.set("state", state);
  } else {
    nextSearchParams.delete("state");
  }

  if (status) {
    nextSearchParams.set("status", status);
  } else {
    nextSearchParams.delete("status");
  }

  const nextQuery = nextSearchParams.toString();

  if (nextQuery === searchParams.toString()) {
    onTableLoadingChange(false);
    return;
  }

  onTableLoadingChange(true);
  startTransition(() => {
    router.replace(`${pathname}?${nextQuery}`, { scroll: false });
  });
}
