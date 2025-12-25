"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { TrustScore } from "@/components/ui/trust-score";
import { WrapperIndicator } from "@/components/ui/wrapper-status";
import { NewsletterSignup } from "@/components/newsletter-signup";

export default function HomePage() {
  const [url, setUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<null | {
    isWrapper: boolean;
    confidence: number;
    status: "native" | "fine_tuned" | "rag" | "wrapper";
    signals: Record<string, boolean>;
  }>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setIsAnalyzing(true);
    setResult(null);

    // Simulate analysis (replace with real API call)
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Mock result
    setResult({
      isWrapper: Math.random() > 0.5,
      confidence: Math.floor(Math.random() * 40) + 60,
      status: ["native", "fine_tuned", "rag", "wrapper"][
        Math.floor(Math.random() * 4)
      ] as "native" | "fine_tuned" | "rag" | "wrapper",
      signals: {
        hasVectorDB: Math.random() > 0.5,
        hasFineTuning: Math.random() > 0.5,
        disclosesModel: Math.random() > 0.5,
        directApiDependency: Math.random() > 0.5,
      },
    });

    setIsAnalyzing(false);
  };

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-zinc-200 bg-gradient-to-b from-zinc-50 to-white dark:border-zinc-800 dark:from-zinc-900 dark:to-zinc-950">
        {/* Background pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)] bg-[size:14px_24px]" />

        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8 lg:py-32">
          <div className="mx-auto max-w-3xl text-center">
            {/* Badge */}
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white/80 px-4 py-1.5 text-sm backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/80">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              </span>
              <span className="text-zinc-600 dark:text-zinc-400">
                Now verifying 500+ AI tools
              </span>
            </div>

            {/* Headline */}
            <h1 className="text-balance text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-5xl lg:text-6xl">
              The Trust Engine of the{" "}
              <span className="gradient-text">AI Economy</span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-zinc-600 dark:text-zinc-400">
              Stop guessing. Start verifying. We test AI tools so you don&apos;t
              have to. Detect wrappers, discover native AI, and make decisions
              with confidence.
            </p>

            {/* Wrapper Detector */}
            <Card className="mx-auto mt-10 max-w-xl p-6">
              <h2 className="mb-4 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                🔍 Wrapper Detector
              </h2>
              <form onSubmit={handleAnalyze} className="flex gap-3">
                <Input
                  type="url"
                  placeholder="Paste any AI tool URL..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1"
                />
                <Button type="submit" isLoading={isAnalyzing}>
                  {isAnalyzing ? "Analyzing..." : "Analyze"}
                </Button>
              </form>

              {/* Result */}
              {result && (
                <div className="mt-6 animate-slide-up space-y-4 border-t border-zinc-200 pt-6 dark:border-zinc-800">
                  <div className="flex items-center justify-between">
                    <WrapperIndicator status={result.status} />
                    <TrustScore
                      score={100 - (result.isWrapper ? 40 : 0)}
                      size="sm"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex items-center gap-2">
                      <span
                        className={
                          result.signals.hasVectorDB
                            ? "text-emerald-500"
                            : "text-zinc-400"
                        }
                      >
                        {result.signals.hasVectorDB ? "✓" : "✗"}
                      </span>
                      <span className="text-zinc-600 dark:text-zinc-400">
                        Vector Database
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={
                          result.signals.hasFineTuning
                            ? "text-emerald-500"
                            : "text-zinc-400"
                        }
                      >
                        {result.signals.hasFineTuning ? "✓" : "✗"}
                      </span>
                      <span className="text-zinc-600 dark:text-zinc-400">
                        Fine-Tuning
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={
                          result.signals.disclosesModel
                            ? "text-emerald-500"
                            : "text-zinc-400"
                        }
                      >
                        {result.signals.disclosesModel ? "✓" : "✗"}
                      </span>
                      <span className="text-zinc-600 dark:text-zinc-400">
                        Model Disclosure
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={
                          !result.signals.directApiDependency
                            ? "text-emerald-500"
                            : "text-amber-500"
                        }
                      >
                        {result.signals.directApiDependency ? "⚠" : "✓"}
                      </span>
                      <span className="text-zinc-600 dark:text-zinc-400">
                        {result.signals.directApiDependency
                          ? "Direct API Dep."
                          : "Independent"}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-zinc-500 dark:text-zinc-500">
                    Confidence: {result.confidence}% •{" "}
                    <Link href="/analyze" className="underline">
                      View full report
                    </Link>
                  </p>
                </div>
              )}
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="border-b border-zinc-200 bg-white py-12 dark:border-zinc-800 dark:bg-zinc-950">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
                500+
              </div>
              <div className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                Tools Verified
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
                47%
              </div>
              <div className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                Wrappers Detected
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
                10k+
              </div>
              <div className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                Newsletter Subs
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
                5
              </div>
              <div className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                Verticals Covered
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
              Beyond Discovery. Into Verification.
            </h2>
            <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">
              Other directories list tools. We test them.
            </p>
          </div>

          <div className="mt-16 grid gap-8 md:grid-cols-3">
            {/* Trust Engine */}
            <Card className="p-6">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-100 text-2xl dark:bg-indigo-950">
                🔬
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                Trust Engine
              </h3>
              <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                Autonomous AI agents test every tool. We score reliability,
                transparency, and proprietary value.
              </p>
              <Link
                href="/tools"
                className="mt-4 inline-flex text-sm font-medium text-indigo-600 dark:text-indigo-400"
              >
                Browse verified tools →
              </Link>
            </Card>

            {/* News & Intel */}
            <Card className="p-6">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100 text-2xl dark:bg-purple-950">
                📰
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                News & Intelligence
              </h3>
              <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                Cut through the hype. Our Hype Meter scores every story.
                Vertical-specific coverage for AgTech, Legal, and more.
              </p>
              <Link
                href="/news"
                className="mt-4 inline-flex text-sm font-medium text-indigo-600 dark:text-indigo-400"
              >
                Read latest intel →
              </Link>
            </Card>

            {/* Learn */}
            <Card className="p-6">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-100 text-2xl dark:bg-emerald-950">
                🎓
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                Cohort Learning
              </h3>
              <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                Live courses on building with AI. Architectural patterns, not
                prompting tricks. Get certified.
              </p>
              <Link
                href="/learn"
                className="mt-4 inline-flex text-sm font-medium text-indigo-600 dark:text-indigo-400"
              >
                View courses →
              </Link>
            </Card>
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section
        id="newsletter"
        className="border-t border-zinc-200 bg-zinc-50 py-24 dark:border-zinc-800 dark:bg-zinc-900"
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
              Stay ahead of the curve
            </h2>
            <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">
              Weekly digest of verified tools, honest news, and expert insights.
              No hype. No spam.
            </p>

            <div className="mt-8">
              <NewsletterSignup />
            </div>

            <p className="mt-3 text-xs text-zinc-500 dark:text-zinc-400">
              Join 10,000+ professionals. Unsubscribe anytime.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
