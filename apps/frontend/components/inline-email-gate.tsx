"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface InlineEmailGateProps {
  source: string;
  essaySlug?: string;
}

export function InlineEmailGate({
  source,
  essaySlug,
}: InlineEmailGateProps) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const router = useRouter();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setStatus("loading");
    setErrorMsg(null);
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          source: essaySlug ? `${source}:${essaySlug}` : source,
        }),
      });
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as {
          error?: string;
        };
        setErrorMsg(data.error ?? "Subscription failed.");
        setStatus("error");
        return;
      }
      setStatus("success");
      setEmail("");
      // Worker set the session cookie in the response. Refresh server
      // components so the rest of the essay unlocks immediately.
      router.refresh();
    } catch {
      setErrorMsg("Network error. Try again.");
      setStatus("error");
    }
  };

  return (
    <div
      role="region"
      aria-label="Subscribe to keep reading"
      className="my-10 rounded-xl border border-zinc-200 bg-zinc-50 p-6 dark:border-zinc-800 dark:bg-zinc-900"
    >
      <p className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
        Reading this whole thing?
      </p>
      <p className="mt-2 text-lg font-semibold leading-snug text-zinc-900 dark:text-zinc-100">
        Join the validation list for production-stack AI teardowns.
      </p>
      <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        Public sends start after the content and email gates pass. Free. No
        spam. Unsubscribe in one click.
      </p>

      {status === "success" ? (
        <div className="mt-4 inline-flex items-center gap-2 rounded-md bg-emerald-100 px-3 py-1.5 text-sm font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
          <span aria-hidden>✓</span>
          <span>Confirmation sent — check your inbox.</span>
        </div>
      ) : (
        <form onSubmit={submit} className="mt-4 flex flex-col gap-2 sm:flex-row">
          <Input
            type="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            aria-label="Email address"
            className="flex-1"
          />
          <Button type="submit" isLoading={status === "loading"}>
            Continue reading
          </Button>
        </form>
      )}
      {errorMsg && (
        <p className="mt-2 text-xs text-red-500">{errorMsg}</p>
      )}
    </div>
  );
}
