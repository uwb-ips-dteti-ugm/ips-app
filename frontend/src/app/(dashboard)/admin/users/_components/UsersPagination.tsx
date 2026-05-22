"use client";

import { CursorPagination } from "@/shared/components/CursorPagination";

import {
  writeNextUsersCursor,
  writePreviousUsersCursor,
} from "../_lib/users-list-state";
import { useUsersListNavigation } from "./useUsersListNavigation";

type UsersPaginationProps = {
  cursorId: string;
  hasNext: boolean;
  itemCount: number;
  nextCursorId?: string;
  onTableLoadingChange: (isLoading: boolean) => void;
};

export function UsersPagination({
  cursorId,
  hasNext,
  itemCount,
  nextCursorId,
  onTableLoadingChange,
}: UsersPaginationProps) {
  const { isPending, replaceQuery } =
    useUsersListNavigation(onTableLoadingChange);

  return (
    <CursorPagination
      busy={isPending}
      hasNext={hasNext && Boolean(nextCursorId)}
      hasPrevious={Boolean(cursorId)}
      itemCount={itemCount}
      itemLabel="user"
      onNext={() => {
        if (!nextCursorId) {
          return;
        }

        replaceQuery((searchParams) => {
          writeNextUsersCursor(searchParams, nextCursorId);
        });
      }}
      onPrevious={() =>
        replaceQuery((searchParams) => {
          writePreviousUsersCursor(searchParams);
        })
      }
    />
  );
}
