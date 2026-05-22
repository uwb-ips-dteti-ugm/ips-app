import Image from "next/image";
import Link from "next/link";

export default function NotFoundPage() {
  return (
    <main className="relative flex min-h-dvh overflow-hidden bg-[#0F2854] px-5 py-7 text-white sm:px-8 lg:px-12">
      <div className="pointer-events-none absolute inset-0 opacity-30 bg-[linear-gradient(rgba(189,232,245,0.22)_1px,transparent_1px),linear-gradient(90deg,rgba(189,232,245,0.18)_1px,transparent_1px)] bg-size-[48px_48px]" />
      <div className="relative z-10 flex min-h-[calc(100dvh-3.5rem)] w-full flex-col">
        <header className="flex flex-wrap items-center gap-4">
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
          <div>
            <p className="text-xs font-semibold uppercase text-[#BDE8F5]">
              Ultra-Wide Band
            </p>
            <h1 className="text-xl font-semibold leading-tight sm:text-2xl">
              Indoor Positioning System
            </h1>
          </div>
        </header>

        <section className="flex flex-1 items-center justify-center py-14 text-center">
          <div className="max-w-xl">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#BDE8F5]">
              404
            </p>
            <h2 className="mt-4 text-4xl font-semibold leading-tight sm:text-5xl">
              Page not found
            </h2>
            <p className="mx-auto mt-4 max-w-md text-base leading-7 text-[#D9EEF7]">
              The page you are looking for does not exist or has been moved.
            </p>
            <Link
              href="/"
              className="mt-8 inline-flex h-11 items-center justify-center rounded-md bg-white px-5 text-sm font-semibold text-[#0F2854] transition hover:bg-[#D9EEF7] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#BDE8F5]"
            >
              Go to dashboard
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
