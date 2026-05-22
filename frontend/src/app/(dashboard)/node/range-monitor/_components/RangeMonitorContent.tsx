"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { CursorPagination } from "@/shared/components/CursorPagination";
import { FilterBar } from "@/shared/components/FilterBar";
import { SelectField } from "@/shared/components/FormControls";
import {
  DataTable,
  EmptyTableState,
  TableBadge,
  TableCell,
  TableFrame,
  TableHead,
  TableLoadingOverlay,
  TableViewport,
} from "@/shared/components/Table";

import {
  getRangeMonitorRangesAction,
  type RangeMonitorRange,
} from "../_actions/get-range-monitor-ranges";
import type { RangeMonitorNodeOption } from "../_lib/get-range-monitor-page-data";

const RANGE_MONITOR_LIMIT_OPTIONS = [5, 10, 20, 50];
const RANGE_REFRESH_INTERVAL_MS = 1_000;

type RangeMonitorContentProps = {
  nodes: RangeMonitorNodeOption[];
};

export function RangeMonitorContent({ nodes }: RangeMonitorContentProps) {
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<Date | null>(null);
  const [limit, setLimit] = useState(10);
  const [page, setPage] = useState(0);
  const [rangeByDeviceId, setRangeByDeviceId] = useState<
    Record<string, RangeMonitorRange | null>
  >({});
  const [selectedNodeId, setSelectedNodeId] = useState("");

  const selectedNode = useMemo(
    () => nodes.find((node) => node.id === selectedNodeId) ?? null,
    [nodes, selectedNodeId],
  );
  const peerNodes = useMemo(() => {
    if (!selectedNode) {
      return [];
    }

    return nodes
      .filter(
        (node) =>
          node.id !== selectedNode.id && node.network.id === selectedNode.network.id,
      )
      .sort((left, right) => left.name.localeCompare(right.name));
  }, [nodes, selectedNode]);
  const pageCount = Math.max(1, Math.ceil(peerNodes.length / limit));
  const boundedPage = Math.min(page, pageCount - 1);
  const visiblePeerNodes = useMemo(
    () => peerNodes.slice(boundedPage * limit, boundedPage * limit + limit),
    [boundedPage, limit, peerNodes],
  );
  const visiblePeerDeviceIds = useMemo(
    () => visiblePeerNodes.map((node) => node.deviceId),
    [visiblePeerNodes],
  );
  const visiblePeerKey = visiblePeerDeviceIds.join("\n");
  const resetMonitorState = useCallback(() => {
    setPage(0);
    setRangeByDeviceId({});
    setLastUpdatedAt(null);
    setError(null);
  }, []);
  const handleSelectedNodeChange = useCallback(
    (value: string) => {
      setSelectedNodeId(value);
      resetMonitorState();
    },
    [resetMonitorState],
  );
  const handleLimitChange = useCallback((value: number) => {
    setLimit(value);
    setPage(0);
  }, []);

  const fetchRanges = useCallback(
    async () => {
      if (!selectedNode || visiblePeerDeviceIds.length === 0) {
        return null;
      }

      return getRangeMonitorRangesAction({
        sourceNodeDeviceId: selectedNode.deviceId,
        targetNodeDeviceIds: visiblePeerDeviceIds,
      });
    },
    [selectedNode, visiblePeerDeviceIds],
  );

  useEffect(() => {
    if (!selectedNode || visiblePeerDeviceIds.length === 0) {
      return;
    }

    let cancelled = false;
    let timeoutId: number | undefined;

    async function refresh(showLoading: boolean): Promise<void> {
      if (showLoading) {
        setIsRefreshing(true);
      }

      const result = await fetchRanges();
      if (cancelled) {
        return;
      }

      if (result && !result.ok) {
        setError(result.error);
      }

      if (result?.ok) {
        setError(null);
        setLastUpdatedAt(new Date());
        setRangeByDeviceId((current) => ({
          ...current,
          ...Object.fromEntries(
            result.ranges.map((row) => [row.targetNodeDeviceId, row.range]),
          ),
        }));
      }

      if (showLoading) {
        setIsRefreshing(false);
      }

      if (!cancelled) {
        timeoutId = window.setTimeout(() => {
          void refresh(false);
        }, RANGE_REFRESH_INTERVAL_MS);
      }
    }

    void refresh(true);

    return () => {
      cancelled = true;
      if (timeoutId !== undefined) {
        window.clearTimeout(timeoutId);
      }
    };
  }, [fetchRanges, selectedNode, visiblePeerKey, visiblePeerDeviceIds.length]);

  return (
    <>
      <FilterBar>
        <SelectField
          id="range-monitor-node"
          label="Node"
          name="node_id"
          value={selectedNodeId}
          onChange={(event) => handleSelectedNodeChange(event.currentTarget.value)}
          className="min-w-[260px] flex-1"
        >
          <option value="">Select a node</option>
          {nodes.map((node) => (
            <option key={node.id} value={node.id}>
              {node.name} ({node.deviceId})
            </option>
          ))}
        </SelectField>

        <SelectField
          id="range-monitor-limit"
          label="Entries"
          name="limit"
          value={String(limit)}
          onChange={(event) =>
            handleLimitChange(Number.parseInt(event.currentTarget.value, 10))
          }
          className="w-24"
        >
          {RANGE_MONITOR_LIMIT_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </SelectField>
      </FilterBar>

      <TableFrame>
        <TableViewport>
          <RangeMonitorTable
            nodes={visiblePeerNodes}
            rangeByDeviceId={rangeByDeviceId}
            selectedNode={selectedNode}
          />
          {isRefreshing && selectedNode && visiblePeerNodes.length > 0 ? (
            <TableLoadingOverlay label="Loading ranges" />
          ) : null}
        </TableViewport>

        <div className="border-t border-[#D9EEF7] px-4 py-2 text-xs font-medium text-[#4988C4] dark:border-[#1C4D8D] dark:text-[#BDE8F5]">
          {selectedNode ? (
            <span>
              {error
                ? error
                : `Refreshes every second${
                    lastUpdatedAt ? ` - Last updated ${formatTime(lastUpdatedAt)}` : ""
                  }`}
            </span>
          ) : (
            <span>Select a node to start monitoring ranges.</span>
          )}
        </div>

        <CursorPagination
          busy={isRefreshing}
          hasNext={boundedPage < pageCount - 1}
          hasPrevious={boundedPage > 0}
          itemCount={visiblePeerNodes.length}
          itemLabel="range"
          onNext={() => setPage((current) => Math.min(current + 1, pageCount - 1))}
          onPrevious={() => setPage((current) => Math.max(current - 1, 0))}
        />
      </TableFrame>
    </>
  );
}

function RangeMonitorTable({
  nodes,
  rangeByDeviceId,
  selectedNode,
}: {
  nodes: RangeMonitorNodeOption[];
  rangeByDeviceId: Record<string, RangeMonitorRange | null>;
  selectedNode: RangeMonitorNodeOption | null;
}) {
  if (!selectedNode) {
    return <EmptyTableState message="Select a node to view live ranges." />;
  }

  if (nodes.length === 0) {
    return <EmptyTableState message="No other approved nodes in this network." />;
  }

  return (
    <DataTable>
      <thead className="bg-[#EAF6FB] text-xs uppercase text-[#1C4D8D] dark:bg-[#0B1E38] dark:text-[#BDE8F5]">
        <tr>
          <TableHead>Target Node</TableHead>
          <TableHead>Device ID</TableHead>
          <TableHead>Address</TableHead>
          <TableHead>Distance</TableHead>
          <TableHead>Direction</TableHead>
          <TableHead>Last Update</TableHead>
        </tr>
      </thead>
      <tbody>
        {nodes.map((node) => {
          const range = rangeByDeviceId[node.deviceId] ?? null;
          return (
            <tr
              key={node.id}
              className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
            >
              <TableCell>
                <div className="max-w-64 truncate font-semibold text-[#0F2854] dark:text-white">
                  {node.name}
                </div>
              </TableCell>
              <TableCell>{node.deviceId}</TableCell>
              <TableCell>{formatAddress(node.address)}</TableCell>
              <TableCell>{range ? `${range.distance.toFixed(3)} m` : "-"}</TableCell>
              <TableCell>
                {range ? (
                  <DirectionBadge range={range} selectedNode={selectedNode} />
                ) : (
                  "-"
                )}
              </TableCell>
              <TableCell>
                {range ? formatTimestamp(range.recordedAt) : "Waiting"}
              </TableCell>
            </tr>
          );
        })}
      </tbody>
    </DataTable>
  );
}

function DirectionBadge({
  range,
  selectedNode,
}: {
  range: RangeMonitorRange;
  selectedNode: RangeMonitorNodeOption;
}) {
  const isOutgoing = range.sourceNodeDeviceId === selectedNode.deviceId;

  return (
    <TableBadge className="border-[#4988C4]/40 bg-[#BDE8F5]/50 text-[#0F2854] dark:text-[#BDE8F5]">
      {isOutgoing ? "Outgoing" : "Incoming"}
    </TableBadge>
  );
}

function formatAddress(value: number): string {
  return `0x${value.toString(16).padStart(4, "0").toUpperCase()} (${value})`;
}

function formatTime(value: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(value);
}

function formatTimestamp(value: string): string {
  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(timestamp);
}
