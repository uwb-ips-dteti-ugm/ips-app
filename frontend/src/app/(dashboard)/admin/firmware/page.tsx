import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import { AccessDenied, PageContent, PageHeader } from "@/shared/components/PageHeader";

import { FirmwareListContent } from "./_components/FirmwareListContent";
import { getFirmwarePageData } from "./_lib/get-firmware-page-data";

export default async function FirmwarePage() {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const data = await getFirmwarePageData(session.accessToken);

  if (!data.canViewFirmware) {
    return <AccessDenied message="Your account does not have access to view firmware." />;
  }

  return (
    <PageContent>
      <PageHeader
        title="Firmware"
        subtitle="Uploaded firmware versions. Upload new builds with firmware/scripts/upload_firmware.py, then deploy them to connected nodes here."
      />

      <FirmwareListContent
        canDeleteFirmware={data.canDeleteFirmware}
        canManageFirmware={data.canManageFirmware}
        connectedNodeCount={data.connectedNodeCount}
        firmwares={data.firmwares}
      />
    </PageContent>
  );
}
