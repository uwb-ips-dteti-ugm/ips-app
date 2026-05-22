import { redirect } from "next/navigation";

import { hasAuthSession } from "@/lib/auth/session";

export default async function SignInLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  if (await hasAuthSession()) {
    redirect("/");
  }

  return children;
}
