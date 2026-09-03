import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";
import {
  AccessDenied,
  PageContent,
  PageHeader,
} from "@/shared/components/PageHeader";

import { MapContent } from "./_components/MapContent";
import { getMapPageData } from "./_lib/get-map-page-data";

export default async function MapPage() {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  const data = await getMapPageData(session.accessToken);

  if (!data.canViewMap) {
    return (
      <AccessDenied message="Your account does not have access to view the map." />
    );
  }

  return (
    <PageContent>
      <PageHeader
        title="Map"
        subtitle="Live position of the mobile node, trilaterated from its distance to the surveyed anchors."
      />

      <MapContent anchors={data.anchors} tagCandidates={data.tagCandidates} />
    </PageContent>
  );
}
