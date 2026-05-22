"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useTransition } from "react";

type SearchParamsUpdate = (searchParams: URLSearchParams) => void;

export function useUsersListNavigation(
  onTableLoadingChange: (isLoading: boolean) => void,
) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  const replaceQuery = useCallback(
    (update: SearchParamsUpdate) => {
      const nextSearchParams = new URLSearchParams(searchParams.toString());
      update(nextSearchParams);

      const nextQuery = nextSearchParams.toString();
      if (nextQuery === searchParams.toString()) {
        onTableLoadingChange(false);
        return;
      }

      onTableLoadingChange(true);
      startTransition(() => {
        router.replace(nextQuery ? `${pathname}?${nextQuery}` : pathname, {
          scroll: false,
        });
      });
    },
    [onTableLoadingChange, pathname, router, searchParams],
  );

  return {
    isPending,
    replaceQuery,
  };
}
