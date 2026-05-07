import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

const TITLE = "aboutai — One honest AI tool teardown a week";
const DESCRIPTION =
  "I run 30 AI-native startups. Every Friday I publish a long-form teardown of one tool I'm actually paying for, with screenshots, configs, latency numbers, and a verdict. No affiliates, no hype.";
const SITE_URL = "https://aboutai.com";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: TITLE,
    template: "%s · 30stacks",
  },
  description: DESCRIPTION,
  authors: [{ name: "Rakesh Roushan", url: "https://x.com/rakesh1002" }],
  creator: "Rakesh Roushan",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: SITE_URL,
    siteName: "aboutai",
    title: TITLE,
    description: DESCRIPTION,
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
    creator: "@rakesh1002",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} min-h-screen bg-white font-sans text-zinc-900 antialiased dark:bg-zinc-950 dark:text-zinc-100`}
      >
        <div className="relative flex min-h-screen flex-col">
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
