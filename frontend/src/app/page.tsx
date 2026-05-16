import { redirect } from "next/navigation";

import { getAuthSession } from "@/lib/auth/session";

import { signOutAction } from "./_actions/sign-out";
import { SignOutButton } from "./_components/SignOutButton";

export default async function Home() {
  const session = await getAuthSession();

  if (!session) {
    redirect("/sign-in");
  }

  return (
    <main className="min-h-dvh bg-white p-6 text-[#0F2854] dark:bg-black dark:text-white">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">IPS App</h1>
          <p className="text-sm text-[#1C4D8D] dark:text-[#BDE8F5]">
            Signed in as {session.claims.name}
          </p>
        </div>

        <form action={signOutAction}>
          <SignOutButton />
        </form>
      </div>
    </main>
  );
}
