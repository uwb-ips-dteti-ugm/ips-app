import Image from "next/image";

import { SignInForm } from "./_components/SignInForm";

export default function SignInPage() {
  return (
    <main className="grid min-h-dvh bg-white text-[#0F2854] lg:grid-cols-[minmax(0,1fr)_520px] dark:bg-black dark:text-white">
      <section className="relative hidden overflow-hidden bg-[#0F2854] px-12 py-10 text-white lg:flex lg:flex-col">
        <div className="pointer-events-none absolute inset-0 opacity-30 bg-[linear-gradient(rgba(189,232,245,0.22)_1px,transparent_1px),linear-gradient(90deg,rgba(189,232,245,0.18)_1px,transparent_1px)] bg-size-[48px_48px]" />
        <div className="relative flex items-center gap-4">
          <Image
            src="/app-logo-light.svg"
            alt="IPS App"
            width={48}
            height={48}
            priority
          />
          <Image
            src="/lambang-ugm-putih.png"
            alt="Universitas Gadjah Mada"
            width={44}
            height={46}
            style={{ height: "auto" }}
            priority
          />
        </div>

        <div className="relative mt-[46vh] max-w-xl">
          <p className="mb-4 text-sm font-semibold uppercase text-[#BDE8F5]">
            Ultra-Wide Band
          </p>
          <h1 className="max-w-lg text-5xl font-semibold leading-[1.08]">
            Indoor Positioning System
          </h1>
        </div>
      </section>

      <section className="flex min-h-dvh items-center justify-center bg-[#F5FAFD] px-5 py-8 sm:px-8 lg:min-h-0 dark:bg-[#02060B]">
        <div className="w-full max-w-100 rounded-lg border border-[#D9EEF7] bg-white p-6 shadow-[0_24px_80px_rgba(15,40,84,0.12)] sm:p-8 dark:border-[#1C4D8D] dark:bg-[#07111F] dark:shadow-none">
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <Image
              className="dark:hidden"
              src="/app-logo-dark.svg"
              alt="IPS App"
              width={44}
              height={44}
              priority
            />
            <Image
              className="hidden dark:block"
              src="/app-logo-light.svg"
              alt="IPS App"
              width={44}
              height={44}
              priority
            />
            <div>
              <div className="text-lg font-semibold text-[#0F2854] dark:text-white">
                Indoor Positioning System
              </div>
              <div className="text-sm text-[#1C4D8D] dark:text-[#BDE8F5]">
                Sign in
              </div>
            </div>
          </div>

          <SignInForm />
        </div>
      </section>
    </main>
  );
}
