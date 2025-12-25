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

export const metadata: Metadata = {
  title: {
    default: "aboutai — The Trust Engine of the AI Economy",
    template: "%s | aboutai",
  },
  description:
    "The definitive source of truth for AI tools. Verified listings, investigative news, and cohort-based learning. Detect wrappers, discover native AI.",
  keywords: [
    "AI tools",
    "artificial intelligence",
    "AI directory",
    "wrapper detector",
    "AI news",
    "trust score",
    "AI verification",
  ],
  authors: [{ name: "aboutai" }],
  creator: "aboutai",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://aboutai.com",
    siteName: "aboutai",
    title: "aboutai — The Trust Engine of the AI Economy",
    description:
      "The definitive source of truth for AI tools. Verified listings, investigative news, and cohort-based learning.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "aboutai",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "aboutai — The Trust Engine of the AI Economy",
    description:
      "The definitive source of truth for AI tools. Verified listings, investigative news, and cohort-based learning.",
    images: ["/og-image.png"],
    creator: "@aboutai",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
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
