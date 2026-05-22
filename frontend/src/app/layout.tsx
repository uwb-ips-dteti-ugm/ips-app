import type { Metadata } from "next";

import { ErrorToastProvider } from "@/shared/components/ErrorToast";

import "./globals.css";

export const metadata: Metadata = {
  title: "IPS App",
  description: "Indoor Positioning System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col">
        <ErrorToastProvider>{children}</ErrorToastProvider>
      </body>
    </html>
  );
}
