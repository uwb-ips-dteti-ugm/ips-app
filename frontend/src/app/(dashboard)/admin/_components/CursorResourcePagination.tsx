"use client";

import { CursorPagination } from "@/shared/components/CursorPagination";

import {
  writeNextCursor,
  writePreviousCursor,
} from "../_lib/cursor-list-state";
import { useCursorListNavigation } from "../_hooks/use-cursor-list-navigation";

type CursorResourcePaginationProps = {
  cursorId: string;
  hasNext: boolean;
  itemCount: number;
  itemLabel: string;
  nextCursorId?: string;
  onTableLoadingChange: (isLoading: boolean) => void;
};

export function CursorResourcePagination({
  cursorId,
  hasNext,
  itemCount,
  itemLabel,
  nextCursorId,
  onTableLoadingChange,
}: CursorResourcePaginationProps) {
  const { isPending, replaceQuery } =
    useCursorListNavigation(onTableLoadingChange);

  return (
    <CursorPagination
      busy={isPending}
      hasNext={hasNext && Boolean(nextCursorId)}
      hasPrevious={Boolean(cursorId)}
      itemCount={itemCount}
      itemLabel={itemLabel}
      onNext={() => {
        if (!nextCursorId) {
          return;
        }

        replaceQuery((searchParams) => {
          writeNextCursor(searchParams, nextCursorId);
        });
      }}
      onPrevious={() =>
        replaceQuery((searchParams) => {
          writePreviousCursor(searchParams);
        })
      }
    />
  );
}
