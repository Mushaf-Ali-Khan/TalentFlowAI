import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

import { QueryProvider } from "@/lib/providers/query-provider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
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
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable}`}
    >
      <body className="antialiased min-h-screen bg-gray-50 text-gray-900 font-sans">
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}