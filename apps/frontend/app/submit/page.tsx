"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

type SubmissionStatus = "idle" | "submitting" | "success" | "error";

export default function SubmitToolPage() {
  const [url, setUrl] = useState("");
  const [email, setEmail] = useState("");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<SubmissionStatus>("idle");
  const [submissionId, setSubmissionId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setStatus("submitting");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/tools/submit`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url,
            submitter_email: email || null,
            notes: notes || null,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSubmissionId(data.submission_id);
        setStatus("success");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  if (status === "success") {
    return (
      <div className="min-h-[70vh] flex items-center justify-center px-4">
        <Card className="max-w-lg w-full p-8 text-center animate-slide-up">
          <div className="mx-auto w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-3xl mb-6">
            ✓
          </div>
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-3">
            Tool Submitted!
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400 mb-6">
            Thanks for contributing to aboutai! Our AI agents will analyze your
            submission and verify it within 24-48 hours.
          </p>
          {submissionId && (
            <p className="text-sm text-zinc-500 dark:text-zinc-500 font-mono mb-6">
              Submission ID: {submissionId}
            </p>
          )}
          <div className="flex gap-4 justify-center">
            <Button variant="outline" onClick={() => setStatus("idle")}>
              Submit Another
            </Button>
            <Link href="/tools">
              <Button>Browse Tools</Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      {/* Header */}
      <section className="relative overflow-hidden border-b border-zinc-200 bg-gradient-to-b from-indigo-50 to-white dark:border-zinc-800 dark:from-indigo-950/30 dark:to-zinc-950">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)] bg-[size:14px_24px]" />
        <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h1 className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-5xl">
              Submit an AI Tool
            </h1>
            <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">
              Help us build the most comprehensive AI tool directory. Submit a
              tool and our AI agents will verify and list it.
            </p>
          </div>
        </div>
      </section>

      {/* Form */}
      <section className="py-16">
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8">
          <Card className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* URL Field */}
              <div>
                <label
                  htmlFor="url"
                  className="block text-sm font-medium text-zinc-900 dark:text-zinc-100 mb-2"
                >
                  Tool URL <span className="text-red-500">*</span>
                </label>
                <Input
                  id="url"
                  type="url"
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                  className="w-full"
                />
                <p className="mt-1.5 text-xs text-zinc-500">
                  Enter the main website URL of the AI tool
                </p>
              </div>

              {/* Email Field */}
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-zinc-900 dark:text-zinc-100 mb-2"
                >
                  Your Email{" "}
                  <span className="text-zinc-400">(optional)</span>
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full"
                />
                <p className="mt-1.5 text-xs text-zinc-500">
                  We&apos;ll notify you when your submission is reviewed
                </p>
              </div>

              {/* Notes Field */}
              <div>
                <label
                  htmlFor="notes"
                  className="block text-sm font-medium text-zinc-900 dark:text-zinc-100 mb-2"
                >
                  Additional Notes{" "}
                  <span className="text-zinc-400">(optional)</span>
                </label>
                <textarea
                  id="notes"
                  placeholder="Any additional context about the tool..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={4}
                  className="w-full rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                />
              </div>

              {/* Error State */}
              {status === "error" && (
                <div className="p-4 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900">
                  <p className="text-sm text-red-600 dark:text-red-400">
                    Something went wrong. Please try again or contact us if the
                    problem persists.
                  </p>
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                isLoading={status === "submitting"}
                size="lg"
              >
                {status === "submitting" ? "Submitting..." : "Submit Tool"}
              </Button>
            </form>
          </Card>

          {/* Info Cards */}
          <div className="mt-12 grid gap-6 sm:grid-cols-3">
            <div className="text-center">
              <div className="mx-auto w-12 h-12 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center text-xl mb-3">
                🤖
              </div>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
                AI Verification
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Our AI agents automatically analyze and verify every submission
              </p>
            </div>
            <div className="text-center">
              <div className="mx-auto w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-xl mb-3">
                ⏱️
              </div>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
                24-48 Hour Review
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Most submissions are reviewed and listed within 2 business days
              </p>
            </div>
            <div className="text-center">
              <div className="mx-auto w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-xl mb-3">
                🔬
              </div>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
                Trust Score
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Each tool gets a trust score based on our proprietary analysis
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="border-t border-zinc-200 dark:border-zinc-800 py-16 bg-zinc-50 dark:bg-zinc-900">
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-8 text-center">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                What makes a tool eligible for listing?
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                We list AI tools that use artificial intelligence or machine
                learning as a core feature. This includes chatbots, code
                assistants, image generators, and specialized AI applications.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                Do you accept wrapper tools?
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Yes, but we&apos;re transparent about it. All tools receive our
                wrapper analysis, and users can see whether a tool is native,
                fine-tuned, RAG-based, or a thin wrapper.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                Is submission free?
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Yes, basic listing is completely free. We offer premium
                placement and featured listings for tools that want additional
                visibility.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

