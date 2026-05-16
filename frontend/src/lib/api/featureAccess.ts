import { apiBaseUrl, getAuthHeaders } from "./client";

type FeatureAccessResponse = {
  feature_name: string;
  can_access: boolean;
};

export async function canAccessFeature(
  accessToken: string,
  featureName: string,
): Promise<boolean> {
  const url = new URL("/users/me/features/access", apiBaseUrl);
  url.searchParams.set("feature_name", featureName);

  try {
    const response = await fetch(url, {
      headers: getAuthHeaders(accessToken),
      cache: "no-store",
    });

    if (!response.ok) {
      return false;
    }

    const data = (await response.json()) as FeatureAccessResponse;
    return data.can_access;
  } catch {
    return false;
  }
}
