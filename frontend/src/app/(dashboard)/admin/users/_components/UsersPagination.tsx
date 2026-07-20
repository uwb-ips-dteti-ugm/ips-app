"use client";

import { Pagination } from "@/shared/components/Pagination";

import {
  writeNextUsersPage,
  writePreviousUsersPage,
} from "../_lib/users-list-state";
import { useListNavigation } from "../../_hooks/use-list-navigation";

type UsersPaginationProps = {
  itemCount: number;
  limit: number;
  onTableLoadingChange: (isLoading: boolean) => void;
  page: number;
  total: number;
};

export function UsersPagination({
  itemCount,
  limit,
  onTableLoadingChange,
  page,
  total,
}: UsersPaginationProps) {
  const { isPending, replaceQuery } = useListNavigation(onTableLoadingChange);

  return (
    <Pagination
      busy={isPending}
      hasNext={(page + 1) * limit < total}
      hasPrevious={page > 0}
      itemCount={itemCount}
      itemLabel="user"
      onNext={() =>
        replaceQuery((searchParams) => {
          writeNextUsersPage(searchParams, page);
        })
      }
      onPrevious={() =>
        replaceQuery((searchParams) => {
          writePreviousUsersPage(searchParams, page);
        })
      }
    />
  );
}
