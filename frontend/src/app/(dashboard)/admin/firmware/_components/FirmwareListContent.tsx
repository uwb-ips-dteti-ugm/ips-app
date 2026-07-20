"use client";

import { useState } from "react";

import type { FirmwareResponse } from "@/lib/api/firmware";
import refreshIcon from "@/shared/assets/RefreshIcon.svg";
import trashIcon from "@/shared/assets/TrashIcon.svg";
import { IconActionButton, TableFrame, TableViewport } from "@/shared/components/Table";

import { DeleteFirmwareModal, DeployFirmwareModal } from "./FirmwareActionModals";
import { FirmwareTable } from "./FirmwareTable";

type FirmwareListContentProps = {
  canDeleteFirmware: boolean;
  canManageFirmware: boolean;
  connectedNodeCount: number;
  firmwares: FirmwareResponse[];
};

type ActiveFirmwareModal =
  | {
      type: "deploy";
      firmware: FirmwareResponse;
    }
  | {
      type: "delete";
      firmware: FirmwareResponse;
    }
  | null;

export function FirmwareListContent({
  canDeleteFirmware,
  canManageFirmware,
  connectedNodeCount,
  firmwares,
}: FirmwareListContentProps) {
  const [activeModal, setActiveModal] = useState<ActiveFirmwareModal>(null);

  return (
    <>
      <TableFrame>
        <TableViewport>
          <FirmwareTable
            firmwares={firmwares}
            renderActions={(firmware) => (
              <>
                {canManageFirmware ? (
                  <IconActionButton
                    icon={refreshIcon}
                    label="Deploy to connected nodes"
                    onClick={() => setActiveModal({ type: "deploy", firmware })}
                  />
                ) : null}
                {canDeleteFirmware ? (
                  <IconActionButton
                    icon={trashIcon}
                    label="Delete"
                    onClick={() => setActiveModal({ type: "delete", firmware })}
                    variant="danger"
                  />
                ) : null}
              </>
            )}
          />
        </TableViewport>
      </TableFrame>

      {activeModal?.type === "deploy" ? (
        <DeployFirmwareModal
          connectedNodeCount={connectedNodeCount}
          firmware={activeModal.firmware}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
      {activeModal?.type === "delete" ? (
        <DeleteFirmwareModal
          firmware={activeModal.firmware}
          onClose={() => setActiveModal(null)}
        />
      ) : null}
    </>
  );
}
