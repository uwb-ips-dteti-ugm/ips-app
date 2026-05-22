"use client";

import { useEffect, useState } from "react";

import { FilterBar } from "@/shared/components/FilterBar";
import { SelectField, TextField } from "@/shared/components/FormControls";

import { useCursorListNavigation } from "../../../admin/_hooks/use-cursor-list-navigation";
import { LIST_LIMIT_OPTIONS } from "../../../admin/_lib/cursor-list-state";
import type { NodeNetworkFilterOption } from "../_lib/get-nodes-page-data";
import {
  parseAddressFilter,
  type NodesListFilters,
  writeNodesListFilters,
} from "../_lib/nodes-list-state";
import { RefreshNodesButton } from "./RefreshNodesButton";

const SEARCH_DEBOUNCE_MS = 400;

type NodesFilterBarProps = {
  filters: NodesListFilters;
  networks: NodeNetworkFilterOption[];
  onTableLoadingChange: (isLoading: boolean) => void;
};

export function NodesFilterBar({
  filters,
  networks,
  onTableLoadingChange,
}: NodesFilterBarProps) {
  const [addressValue, setAddressValue] = useState(filters.address);
  const [searchValue, setSearchValue] = useState(filters.search);
  const { replaceQuery } = useCursorListNavigation(onTableLoadingChange);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      const address = parseAddressFilter(addressValue);
      const search = searchValue.trim();
      if (
        address === null ||
        (address === filters.address && search === filters.search)
      ) {
        return;
      }

      replaceFilters(replaceQuery, {
        ...filters,
        address,
        search,
      });
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timeout);
  }, [addressValue, filters, replaceQuery, searchValue]);

  return (
    <FilterBar>
      <TextField
        id="nodes-search"
        label="Search"
        name="search"
        type="search"
        value={searchValue}
        onChange={(event) => setSearchValue(event.currentTarget.value)}
        placeholder="Search node names or device IDs"
        className="min-w-55 flex-1"
        inputClassName="w-full"
      />

      <SelectField
        id="nodes-status"
        label="Status"
        name="status"
        value={filters.status}
        onChange={(event) =>
          replaceFilters(replaceQuery, {
            ...filters,
            status: event.currentTarget.value as NodesListFilters["status"],
          })
        }
        className="min-w-37.5 basis-40"
      >
        <option value="">All statuses</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="suspended">Suspended</option>
        <option value="revoked">Revoked</option>
      </SelectField>

      <SelectField
        id="nodes-connection"
        label="Connection"
        name="is_online"
        value={filters.isOnline}
        onChange={(event) =>
          replaceFilters(replaceQuery, {
            ...filters,
            isOnline: event.currentTarget.value as NodesListFilters["isOnline"],
          })
        }
        className="min-w-37.5 basis-40"
      >
        <option value="">All connections</option>
        <option value="true">Online</option>
        <option value="false">Offline</option>
      </SelectField>

      <SelectField
        id="nodes-network"
        label="Network"
        name="network_id"
        value={filters.networkId}
        onChange={(event) =>
          replaceFilters(replaceQuery, {
            ...filters,
            networkId: event.currentTarget.value,
          })
        }
        className="min-w-47.5 basis-60"
      >
        <option value="">All networks</option>
        {networks.map((network) => (
          <option key={network.id} value={network.id}>
            {network.name}
          </option>
        ))}
      </SelectField>

      <TextField
        id="nodes-address"
        label="Address"
        name="address"
        type="number"
        inputMode="numeric"
        min={0}
        max={0xffff}
        step={1}
        value={addressValue}
        onChange={(event) => setAddressValue(event.currentTarget.value)}
        placeholder="All"
        className="w-28"
        inputClassName="w-full"
      />

      <SelectField
        id="nodes-limit"
        label="Entries"
        name="limit"
        value={String(filters.limit)}
        onChange={(event) =>
          replaceFilters(replaceQuery, {
            ...filters,
            limit: Number.parseInt(event.currentTarget.value, 10),
          })
        }
        className="w-24"
      >
        {LIST_LIMIT_OPTIONS.map((limit) => (
          <option key={limit} value={limit}>
            {limit}
          </option>
        ))}
      </SelectField>

      <RefreshNodesButton />
    </FilterBar>
  );
}

function replaceFilters(
  replaceQuery: ReturnType<typeof useCursorListNavigation>["replaceQuery"],
  filters: NodesListFilters,
) {
  replaceQuery((searchParams) => {
    writeNodesListFilters(searchParams, filters);
  });
}
