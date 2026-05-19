import type { Metadata } from "next";
import { Space_Grotesk, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

import { ClerkProvider } from "@clerk/nextjs";
import { QueryProvider } from "@/lib/providers/query-provider";
import { ApiClientProvider } from "@/lib/providers/api-client-provider";
import { ToastProvider } from "@/lib/providers/toast-provider";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "600"],
  variable: "--font-ibm-plex-mono",
});

export const metadata: Metadata = {
  title: "TalentFlow AI",
  description: "AI-Assisted Hiring Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html
        lang="en"
        className={`${spaceGrotesk.variable} ${ibmPlexMono.variable}`}
      >
        <body className="antialiased min-h-screen bg-[var(--tf-bg)] text-[var(--tf-ink)] font-sans">
          <ApiClientProvider>
            <ToastProvider>
              <QueryProvider>
                {children}
              </QueryProvider>
            </ToastProvider>
          </ApiClientProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
