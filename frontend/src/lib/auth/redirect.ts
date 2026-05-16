export function getSafeRedirectPath(value: FormDataEntryValue | string | null): string {
  if (typeof value !== "string") {
    return "/";
  }

  if (!value.startsWith("/") || value.startsWith("//")) {
    return "/";
  }

  return value;
}
