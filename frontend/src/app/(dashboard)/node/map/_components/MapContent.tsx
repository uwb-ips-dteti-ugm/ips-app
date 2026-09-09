"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { FilterBar } from "@/shared/components/FilterBar";
import { SelectField, TextField } from "@/shared/components/FormControls";
import type { Point2D } from "@/lib/utils/trilateration";

import {
  type AnchorRangeReading,
  getTagPositionAction,
} from "../_actions/get-tag-position";
import { getTagPositionHistoryAction } from "../_actions/get-tag-position-history";
import type { MapAnchorNode, MapTagCandidate } from "../_lib/get-map-page-data";
import {
  DEFAULT_TAG_HEIGHT_M,
  LAB_DASAR_BOUNDS,
  LAB_DASAR_ROOM_POLYGON,
} from "../_lib/lab-dasar-room";

const POSITION_REFRESH_INTERVAL_MS = 500;
const HISTORY_REFRESH_INTERVAL_MS = 3_000;
const VIEWPORT_PADDING_M = 1.2;
const STALE_READING_MS = 5_000;

// How long a comet-tail point stays visible before fully fading out. Kept
// short (recent motion only) -- the separate "history" line is what shows
// the complete persisted path.
const TRAIL_FADE_MS = 10_000;

type ViewMode = "trail" | "history";

// Glides the marker between polls instead of snapping to each new point --
// kept a bit under POSITION_REFRESH_INTERVAL_MS so a transition always
// finishes before the next update arrives.
const POSITION_TRANSITION_STYLE = {
  transition: "cx 0.45s linear, cy 0.45s linear, x 0.45s linear, y 0.45s linear",
};

type TrailPoint = Point2D & { at: number };

type MapContentProps = {
  anchors: MapAnchorNode[];
  tagCandidates: MapTagCandidate[];
};

export function MapContent({ anchors, tagCandidates }: MapContentProps) {
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("trail");
  const [historyPoints, setHistoryPoints] = useState<Point2D[]>([]);
  const [historySince, setHistorySince] = useState(() => new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<Date | null>(null);
  const [position, setPosition] = useState<Point2D | null>(null);
  const [readings, setReadings] = useState<AnchorRangeReading[]>([]);
  const [selectedTagId, setSelectedTagId] = useState(
    tagCandidates[0]?.id ?? "",
  );
  const [tagHeightInput, setTagHeightInput] = useState(
    String(DEFAULT_TAG_HEIGHT_M),
  );
  const [trail, setTrail] = useState<TrailPoint[]>([]);

  const tagHeight = useMemo(() => {
    const parsed = Number.parseFloat(tagHeightInput);
    return Number.isFinite(parsed) ? parsed : DEFAULT_TAG_HEIGHT_M;
  }, [tagHeightInput]);

  const handleSelectedTagChange = useCallback((value: string) => {
    setSelectedTagId(value);
    setPosition(null);
    setReadings([]);
    setLastUpdatedAt(null);
    setError(null);
    setTrail([]);
    setHistoryPoints([]);
    setHistorySince(new Date());
  }, []);

  useEffect(() => {
    if (!selectedTagId || anchors.length === 0) {
      return;
    }

    let cancelled = false;
    let timeoutId: number | undefined;

    async function refresh(showLoading: boolean): Promise<void> {
      if (showLoading) {
        setIsRefreshing(true);
      }

      const result = await getTagPositionAction({
        anchors,
        tagHeight,
        tagNodeId: selectedTagId,
      });

      if (cancelled) {
        return;
      }

      if (!result.ok) {
        setError(result.error);
      } else {
        setError(null);
        setPosition(result.position);
        setReadings(result.readings);
        const now = Date.now();
        setLastUpdatedAt(new Date(now));
        if (result.position) {
          const newPoint = result.position;
          const cutoff = now - TRAIL_FADE_MS;
          setTrail((current) => [
            ...current.filter((point) => point.at >= cutoff),
            { ...newPoint, at: now },
          ]);
        }
      }

      if (showLoading) {
        setIsRefreshing(false);
      }

      if (!cancelled) {
        timeoutId = window.setTimeout(() => {
          void refresh(false);
        }, POSITION_REFRESH_INTERVAL_MS);
      }
    }

    void refresh(true);

    return () => {
      cancelled = true;
      if (timeoutId !== undefined) {
        window.clearTimeout(timeoutId);
      }
    };
    // `anchors` is a stable prop from the server-rendered page, not
    // per-render state, so it's intentionally left out of the dependency
    // list to avoid restarting the poll loop every render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTagId, tagHeight]);

  useEffect(() => {
    if (viewMode !== "history" || !selectedTagId) {
      return;
    }

    let cancelled = false;
    let timeoutId: number | undefined;

    async function refreshHistory(): Promise<void> {
      const result = await getTagPositionHistoryAction({
        since: historySince,
        tagNodeId: selectedTagId,
      });

      if (cancelled) {
        return;
      }

      if (result.ok) {
        setHistoryPoints(result.points);
      }

      if (!cancelled) {
        timeoutId = window.setTimeout(() => {
          void refreshHistory();
        }, HISTORY_REFRESH_INTERVAL_MS);
      }
    }

    void refreshHistory();

    return () => {
      cancelled = true;
      if (timeoutId !== undefined) {
        window.clearTimeout(timeoutId);
      }
    };
  }, [historySince, selectedTagId, viewMode]);

  if (anchors.length === 0) {
    return (
      <div className="rounded-md border border-[#D9EEF7] bg-white p-6 text-sm text-[#4988C4] dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-[#BDE8F5]">
        None of the three surveyed Lab Dasar anchors are approved and online
        yet. Approve UWB Labdas 1/2/3 on the Nodes page first.
      </div>
    );
  }

  return (
    <>
      <FilterBar>
        <SelectField
          id="map-tag-node"
          label="Mobile Node"
          name="tag_node_id"
          value={selectedTagId}
          onChange={(event) => handleSelectedTagChange(event.currentTarget.value)}
          className="min-w-65 flex-1"
        >
          <option value="">Select a node</option>
          {tagCandidates.map((node) => (
            <option key={node.id} value={node.id}>
              {node.name} ({node.deviceId})
            </option>
          ))}
        </SelectField>

        <TextField
          id="map-tag-height"
          label="Tag Height (m)"
          name="tag_height"
          type="number"
          inputMode="decimal"
          min={0}
          step={0.1}
          value={tagHeightInput}
          onChange={(event) => setTagHeightInput(event.currentTarget.value)}
          className="w-32"
        />

        <SelectField
          id="map-view-mode"
          label="View"
          name="view_mode"
          value={viewMode}
          onChange={(event) => setViewMode(event.currentTarget.value as ViewMode)}
          className="w-40"
        >
          <option value="trail">Trail mode</option>
          <option value="history">Show history</option>
        </SelectField>
      </FilterBar>

      <div className="flex min-h-0 flex-1 gap-4">
        <div className="min-w-0 flex-1 overflow-hidden rounded-md border border-[#D9EEF7] bg-white dark:border-[#1C4D8D] dark:bg-[#07111F]">
          <RoomMap
            anchors={anchors}
            history={viewMode === "history" ? historyPoints : []}
            position={position}
            trail={viewMode === "trail" ? trail : []}
          />
        </div>

        <div className="flex w-72 shrink-0 flex-col gap-3 overflow-y-auto rounded-md border border-[#D9EEF7] bg-white p-4 dark:border-[#1C4D8D] dark:bg-[#07111F]">
          <StatusPanel
            error={error}
            lastUpdatedAt={lastUpdatedAt}
            position={position}
            readings={readings}
            selectedTagId={selectedTagId}
          />
        </div>
      </div>

      <div className="border-t border-[#D9EEF7] px-1 py-2 text-xs font-medium text-[#4988C4] dark:border-[#1C4D8D] dark:text-[#BDE8F5]">
        {selectedTagId ? (
          <span>
            {isRefreshing && !lastUpdatedAt
              ? "Loading..."
              : `Refreshes every second${
                  lastUpdatedAt ? ` - Last updated ${formatTime(lastUpdatedAt)}` : ""
                }`}
          </span>
        ) : (
          <span>Select a mobile node to start tracking its position.</span>
        )}
      </div>
    </>
  );
}

function StatusPanel({
  error,
  lastUpdatedAt,
  position,
  readings,
  selectedTagId,
}: {
  error: string | null;
  lastUpdatedAt: Date | null;
  position: Point2D | null;
  readings: AnchorRangeReading[];
  selectedTagId: string;
}) {
  if (!selectedTagId) {
    return (
      <p className="text-sm text-[#4988C4] dark:text-[#BDE8F5]">
        No mobile node selected.
      </p>
    );
  }

  return (
    <>
      <div>
        <div className="text-xs font-semibold uppercase text-[#4988C4] dark:text-[#BDE8F5]">
          Position
        </div>
        <div className="mt-1 text-lg font-bold text-[#0F2854] dark:text-white">
          {position
            ? `(${position.x.toFixed(2)}, ${position.y.toFixed(2)}) m`
            : "No fix"}
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <div className="text-xs font-semibold uppercase text-[#4988C4] dark:text-[#BDE8F5]">
          Anchor Ranges
        </div>
        {readings.map((reading) => (
          <div
            key={reading.anchorLabel}
            className="flex items-center justify-between rounded-md border border-[#D9EEF7] px-3 py-2 text-sm dark:border-[#1C4D8D]"
          >
            <span className="font-medium text-[#0F2854] dark:text-white">
              {reading.anchorLabel}
            </span>
            <span
              className={
                reading.distance === null || isStale(reading.recordedAt, lastUpdatedAt)
                  ? "text-[#D85858]"
                  : "font-semibold text-[#0F2854] dark:text-white"
              }
            >
              {reading.distance !== null ? `${reading.distance.toFixed(3)} m` : "-"}
            </span>
          </div>
        ))}
      </div>

      {error ? <p className="text-sm text-[#D85858]">{error}</p> : null}
    </>
  );
}

function RoomMap({
  anchors,
  history,
  position,
  trail,
}: {
  anchors: MapAnchorNode[];
  history: Point2D[];
  position: Point2D | null;
  trail: TrailPoint[];
}) {
  const [hoveredAnchorId, setHoveredAnchorId] = useState<string | null>(null);
  const [pinnedAnchorId, setPinnedAnchorId] = useState<string | null>(null);

  const width = LAB_DASAR_BOUNDS.width + VIEWPORT_PADDING_M * 2;
  const height = LAB_DASAR_BOUNDS.height + VIEWPORT_PADDING_M * 2;

  const toViewBox = useCallback(
    (point: Point2D) => ({
      x: point.x + VIEWPORT_PADDING_M,
      y: LAB_DASAR_BOUNDS.height - point.y + VIEWPORT_PADDING_M,
    }),
    [],
  );

  const roomPoints = useMemo(
    () =>
      LAB_DASAR_ROOM_POLYGON.map((point) => {
        const p = toViewBox(point);
        return `${p.x},${p.y}`;
      }).join(" "),
    [toViewBox],
  );

  const gridLines = useMemo(() => {
    const lines: { x1: number; y1: number; x2: number; y2: number }[] = [];
    for (let x = 0; x <= Math.ceil(LAB_DASAR_BOUNDS.width); x += 1) {
      const top = toViewBox({ x, y: LAB_DASAR_BOUNDS.height });
      const bottom = toViewBox({ x, y: 0 });
      lines.push({ x1: top.x, y1: top.y, x2: bottom.x, y2: bottom.y });
    }
    for (let y = 0; y <= Math.ceil(LAB_DASAR_BOUNDS.height); y += 1) {
      const left = toViewBox({ x: 0, y });
      const right = toViewBox({ x: LAB_DASAR_BOUNDS.width, y });
      lines.push({ x1: left.x, y1: left.y, x2: right.x, y2: right.y });
    }
    return lines;
  }, [toViewBox]);

  const positionPixel = position ? toViewBox(position) : null;

  const historyPolylinePoints = useMemo(
    () =>
      history
        .map((point) => {
          const p = toViewBox(point);
          return `${p.x},${p.y}`;
        })
        .join(" "),
    [history, toViewBox],
  );

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="h-full w-full"
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="Lab Dasar floor map"
    >
      <style>{`@keyframes trail-fade { from { opacity: 0.55; } to { opacity: 0; } }`}</style>

      <rect x={0} y={0} width={width} height={height} className="fill-white dark:fill-[#07111F]" />

      <polygon
        points={roomPoints}
        strokeWidth={0.06}
        className="fill-[#EAF6FB] stroke-[#4988C4] dark:fill-[#0B1E38] dark:stroke-[#BDE8F5]"
      />

      {gridLines.map((line, index) => (
        <line
          key={index}
          x1={line.x1}
          y1={line.y1}
          x2={line.x2}
          y2={line.y2}
          strokeWidth={0.01}
          className="stroke-[#BDE8F5] dark:stroke-[#4988C4]"
        />
      ))}

      {history.length >= 2 ? (
        <polyline
          points={historyPolylinePoints}
          fill="none"
          strokeWidth={0.05}
          strokeLinejoin="round"
          strokeLinecap="round"
          className="stroke-[#4988C4] dark:stroke-[#BDE8F5]"
        />
      ) : null}

      {anchors.map((anchor) => {
        const p = toViewBox(anchor);
        const isActive =
          anchor.deviceId === hoveredAnchorId || anchor.deviceId === pinnedAnchorId;

        return (
          <g
            key={anchor.deviceId}
            className="cursor-pointer outline-none"
            style={{ WebkitTapHighlightColor: "transparent" }}
            opacity={anchor.isOffline ? 0.35 : 1}
            tabIndex={-1}
            onMouseEnter={() => setHoveredAnchorId(anchor.deviceId)}
            onMouseLeave={() => setHoveredAnchorId(null)}
            onClick={() =>
              setPinnedAnchorId((current) =>
                current === anchor.deviceId ? null : anchor.deviceId,
              )
            }
          >
            <circle cx={p.x} cy={p.y} r={0.22} className="fill-[#1C4D8D]" />
            <text
              x={p.x}
              y={p.y - 0.32}
              fontSize={0.32}
              textAnchor="middle"
              className="fill-[#0F2854] font-semibold dark:fill-white"
            >
              {anchor.label}
            </text>
            {isActive ? (
              <CoordinateLabel
                x={p.x}
                y={p.y + 0.55}
                text={formatCoordinate(anchor)}
                background="fill-[#1C4D8D]"
                textColor="fill-white"
              />
            ) : null}
          </g>
        );
      })}

      {trail.map((point) => {
        const p = toViewBox(point);
        return (
          <circle
            key={point.at}
            cx={p.x}
            cy={p.y}
            r={0.14}
            style={{ animation: `trail-fade ${TRAIL_FADE_MS}ms linear forwards` }}
            className="fill-[#D85858]"
          />
        );
      })}

      {positionPixel && position ? (
        <g>
          <circle
            cx={positionPixel.x}
            cy={positionPixel.y}
            r={0.28}
            style={POSITION_TRANSITION_STYLE}
            className="animate-pulse fill-[#D85858] stroke-white stroke-[0.06] dark:stroke-[#07111F]"
          />
          <CoordinateLabel
            x={positionPixel.x}
            y={positionPixel.y - 0.55}
            text={formatCoordinate(position)}
            background="fill-[#D85858]"
            textColor="fill-white"
            transition
          />
        </g>
      ) : null}
    </svg>
  );
}

function CoordinateLabel({
  background,
  text,
  textColor,
  transition,
  x,
  y,
}: {
  background: string;
  text: string;
  textColor: string;
  transition?: boolean;
  x: number;
  y: number;
}) {
  const width = text.length * 0.19 + 0.24;
  const style = transition ? POSITION_TRANSITION_STYLE : undefined;

  return (
    <g>
      <rect
        x={x - width / 2}
        y={y - 0.22}
        width={width}
        height={0.44}
        rx={0.08}
        style={style}
        className={background}
      />
      <text
        x={x}
        y={y + 0.11}
        fontSize={0.26}
        textAnchor="middle"
        style={style}
        className={`${textColor} font-semibold`}
      >
        {text}
      </text>
    </g>
  );
}

function formatCoordinate(point: Point2D): string {
  return `(${point.x.toFixed(2)}, ${point.y.toFixed(2)})`;
}

function isStale(recordedAt: string | null, now: Date | null): boolean {
  if (!recordedAt || !now) {
    return true;
  }

  return now.getTime() - new Date(recordedAt).getTime() > STALE_READING_MS;
}

function formatTime(value: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(value);
}
