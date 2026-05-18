"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, useTransition } from "react";

import { type NodeListItem } from "@/lib/api/nodes";
import { FilterBar } from "@/shared/components/FilterBar";
import { SelectField, TextField } from "@/shared/components/FormControls";

const SEARCH_DEBOUNCE_MS = 400;

type RangingPairSelectorProps = {
  sourceSearch: string;
  targetSearch: string;
  sourceNodeDeviceId: string;
  targetNodeDeviceId: string;
  sourceNodes: NodeListItem[];
  targetNodes: NodeListItem[];
};

export function RangingPairSelector({
  sourceSearch,
  targetSearch,
  sourceNodeDeviceId,
  targetNodeDeviceId,
  sourceNodes,
  targetNodes,
}: RangingPairSelectorProps) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [sourceSearchValue, setSourceSearchValue] = useState(sourceSearch);
  const [targetSearchValue, setTargetSearchValue] = useState(targetSearch);
  const [, startTransition] = useTransition();

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      const normalizedSearch = sourceSearchValue.trim();
      if (normalizedSearch === (searchParams.get("source_search") ?? "")) {
        return;
      }

      replaceRangingQuery({
        pathname,
        router,
        searchParams,
        sourceSearch: normalizedSearch,
        targetSearch: targetSearchValue.trim(),
        sourceNodeDeviceId,
        targetNodeDeviceId,
        startTransition,
      });
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timeout);
  }, [
    pathname,
    router,
    searchParams,
    sourceNodeDeviceId,
    sourceSearchValue,
    startTransition,
    targetNodeDeviceId,
    targetSearchValue,
  ]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      const normalizedSearch = targetSearchValue.trim();
      if (normalizedSearch === (searchParams.get("target_search") ?? "")) {
        return;
      }

      replaceRangingQuery({
        pathname,
        router,
        searchParams,
        sourceSearch: sourceSearchValue.trim(),
        targetSearch: normalizedSearch,
        sourceNodeDeviceId,
        targetNodeDeviceId,
        startTransition,
      });
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timeout);
  }, [
    pathname,
    router,
    searchParams,
    sourceNodeDeviceId,
    sourceSearchValue,
    startTransition,
    targetNodeDeviceId,
    targetSearchValue,
  ]);

  return (
    <FilterBar>
      <TextField
        id="source-node-search"
        label="Source Search"
        name="source_search"
        type="search"
        value={sourceSearchValue}
        onChange={(event) => setSourceSearchValue(event.currentTarget.value)}
        placeholder="Search source nodes"
        className="min-w-[220px] flex-1"
        inputClassName="w-full min-w-0"
      />
      <SelectField
        id="source-node"
        label="Source Node"
        name="source_node_device_id"
        value={sourceNodeDeviceId}
        onChange={(event) =>
          replaceRangingQuery({
            pathname,
            router,
            searchParams,
            sourceSearch: sourceSearchValue.trim(),
            targetSearch: targetSearchValue.trim(),
            sourceNodeDeviceId: event.currentTarget.value,
            targetNodeDeviceId,
            startTransition,
          })
        }
        className="min-w-[240px] basis-72"
      >
        <option value="">select source</option>
        {sourceNodes.map((node) => (
          <option key={node.device_id} value={node.device_id}>
            {node.name} ({node.device_id})
          </option>
        ))}
      </SelectField>

      <TextField
        id="target-node-search"
        label="Target Search"
        name="target_search"
        type="search"
        value={targetSearchValue}
        onChange={(event) => setTargetSearchValue(event.currentTarget.value)}
        placeholder="Search target nodes"
        className="min-w-[220px] flex-1"
        inputClassName="w-full min-w-0"
      />
      <SelectField
        id="target-node"
        label="Target Node"
        name="target_node_device_id"
        value={targetNodeDeviceId}
        onChange={(event) =>
          replaceRangingQuery({
            pathname,
            router,
            searchParams,
            sourceSearch: sourceSearchValue.trim(),
            targetSearch: targetSearchValue.trim(),
            sourceNodeDeviceId,
            targetNodeDeviceId: event.currentTarget.value,
            startTransition,
          })
        }
        className="min-w-[240px] basis-72"
      >
        <option value="">select target</option>
        {targetNodes.map((node) => (
          <option key={node.device_id} value={node.device_id}>
            {node.name} ({node.device_id})
          </option>
        ))}
      </SelectField>
    </FilterBar>
  );
}

function replaceRangingQuery({
  pathname,
  router,
  searchParams,
  sourceSearch,
  targetSearch,
  sourceNodeDeviceId,
  targetNodeDeviceId,
  startTransition,
}: {
  pathname: string;
  router: ReturnType<typeof useRouter>;
  searchParams: ReturnType<typeof useSearchParams>;
  sourceSearch: string;
  targetSearch: string;
  sourceNodeDeviceId: string;
  targetNodeDeviceId: string;
  startTransition: (callback: () => void) => void;
}) {
  const nextSearchParams = new URLSearchParams(searchParams.toString());
  setOrDelete(nextSearchParams, "source_search", sourceSearch);
  setOrDelete(nextSearchParams, "target_search", targetSearch);
  setOrDelete(nextSearchParams, "source_node_device_id", sourceNodeDeviceId);
  setOrDelete(nextSearchParams, "target_node_device_id", targetNodeDeviceId);

  const nextQuery = nextSearchParams.toString();
  if (nextQuery === searchParams.toString()) {
    return;
  }

  startTransition(() => {
    router.replace(`${pathname}?${nextQuery}`, { scroll: false });
  });
}

function setOrDelete(
  searchParams: URLSearchParams,
  key: string,
  value: string,
) {
  if (value) {
    searchParams.set(key, value);
  } else {
    searchParams.delete(key);
  }
}
