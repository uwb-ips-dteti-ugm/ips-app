import { type RangingRecord } from "@/lib/api/records";
import { formatDate } from "@/lib/format";

type RangeResultProps = {
  sourceNodeDeviceId: string;
  targetNodeDeviceId: string;
  latestRecord: RangingRecord | null;
};

export function RangeResult({
  sourceNodeDeviceId,
  targetNodeDeviceId,
  latestRecord,
}: RangeResultProps) {
  return (
    <section className="rounded-md border border-[#D9EEF7] bg-white p-5 dark:border-[#1C4D8D] dark:bg-[#07111F]">
      <h2 className="text-base font-semibold text-[#0F2854] dark:text-white">
        Latest Distance
      </h2>

      <div className="mt-4">
        <RangeResultContent
          sourceNodeDeviceId={sourceNodeDeviceId}
          targetNodeDeviceId={targetNodeDeviceId}
          latestRecord={latestRecord}
        />
      </div>
    </section>
  );
}

function RangeResultContent({
  sourceNodeDeviceId,
  targetNodeDeviceId,
  latestRecord,
}: RangeResultProps) {
  if (!sourceNodeDeviceId || !targetNodeDeviceId) {
    return (
      <p className="text-sm text-[#4988C4] dark:text-[#BDE8F5]">
        Select a source node and a target node.
      </p>
    );
  }

  if (sourceNodeDeviceId === targetNodeDeviceId) {
    return (
      <p className="text-sm text-[#9F3A3A] dark:text-[#F3B7B7]">
        Select two different nodes.
      </p>
    );
  }

  if (!latestRecord) {
    return (
      <p className="text-sm text-[#4988C4] dark:text-[#BDE8F5]">
        No ranging record exists for this pair yet.
      </p>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
      <div className="min-w-0">
        <div className="text-4xl font-semibold text-[#0F2854] dark:text-white">
          {latestRecord.data.distance === null
            ? "Unreachable"
            : `${latestRecord.data.distance.toFixed(2)} m`}
        </div>
        <div className="mt-2 text-sm text-[#4988C4] dark:text-[#BDE8F5]">
          {latestRecord.data.source_node_device_id} to{" "}
          {latestRecord.data.target_node_device_id}
        </div>
      </div>
      <dl className="grid gap-2 text-sm">
        <div>
          <dt className="text-xs font-semibold uppercase text-[#4988C4] dark:text-[#BDE8F5]">
            Recorded
          </dt>
          <dd className="mt-1 text-[#0F2854] dark:text-white">
            {formatDate(latestRecord.recorded_at)}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-[#4988C4] dark:text-[#BDE8F5]">
            Record ID
          </dt>
          <dd className="mt-1 font-mono text-xs text-[#0F2854] dark:text-white">
            {latestRecord.id ?? "not available"}
          </dd>
        </div>
      </dl>
    </div>
  );
}
