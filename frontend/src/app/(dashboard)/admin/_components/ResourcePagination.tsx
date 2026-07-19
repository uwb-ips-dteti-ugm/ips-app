"use client";

import { Pagination } from "@/shared/components/Pagination";

import { writeNextPage, writePreviousPage } from "../_lib/page-list-state";
import { useListNavigation } from "../_hooks/use-list-navigation";

type ResourcePaginationProps = {
  itemCount: number;
  itemLabel: string;
  limit: number;
  onTableLoadingChange: (isLoading: boolean) => void;
  page: number;
  total: number;
};

export function ResourcePagination({
  itemCount,
  itemLabel,
  limit,
  onTableLoadingChange,
  page,
  total,
}: ResourcePaginationProps) {
  const { isPending, replaceQuery } = useListNavigation(onTableLoadingChange);

  return (
    <Pagination
      busy={isPending}
      hasNext={(page + 1) * limit < total}
      hasPrevious={page > 0}
      itemCount={itemCount}
      itemLabel={itemLabel}
      onNext={() =>
        replaceQuery((searchParams) => {
          writeNextPage(searchParams, page);
        })
      }
      onPrevious={() =>
        replaceQuery((searchParams) => {
          writePreviousPage(searchParams, page);
        })
      }
    />
  );
}
