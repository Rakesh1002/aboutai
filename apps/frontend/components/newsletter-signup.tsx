"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type SubscribeStatus = "idle" | "loading" | "success" | "error";

interface NewsletterSignupProps {
  variant?: "default" | "minimal" | "card";
  source?: string;
  className?: string;
}

export function NewsletterSignup({
  variant = "default",
  source = "site",
  className = "",
}: NewsletterSignupProps) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<SubscribeStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setStatus("loading");
    setErrorMsg(null);

    try {
      const response = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source }),
      });

      if (response.ok) {
        setStatus("success");
        setEmail("");
        return;
      }

      const data = (await response.json().catch(() => ({}))) as {
        error?: string;
      };
      setErrorMsg(data.error ?? "Subscription failed. Try again.");
      setStatus("error");
    } catch {
      setErrorMsg("Network error. Try again.");
      setStatus("error");
    }
  };

  if (status === "success") {
    return (
      <div className={`text-center ${className}`} id="subscribe">
        <div className="inline-flex items-center gap-2 rounded-full bg-emerald-100 px-4 py-2 text-sm font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
          <span aria-hidden>✓</span>
          <span>Subscribed. Check your inbox.</span>
        </div>
      </div>
    );
  }

  if (variant === "minimal") {
    return (
      <form
        id="subscribe"
        onSubmit={handleSubmit}
        className={`flex flex-col gap-2 sm:flex-row ${className}`}
      >
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
          Subscribe
        </Button>
        {errorMsg && (
          <p className="text-xs text-red-500 sm:absolute sm:mt-12">
            {errorMsg}
          </p>
        )}
      </form>
    );
  }

  if (variant === "card") {
    return (
      <div
        className={`rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900 ${className}`}
        id="subscribe"
      >
        <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
          Join the validation list
        </h3>
        <p className="mt-1 text-sm text-zinc-500">
          Public sends start after the content and email gates pass.
          Unsubscribe in one click.
        </p>
        <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
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
            Join
          </Button>
        </form>
        {errorMsg && <p className="mt-2 text-xs text-red-500">{errorMsg}</p>}
      </div>
    );
  }

  return (
    <div className={className} id="subscribe">
      <form onSubmit={handleSubmit} className="mx-auto flex max-w-md gap-3">
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
          Subscribe
        </Button>
      </form>
      {errorMsg && (
        <p className="mt-2 text-center text-xs text-red-500">{errorMsg}</p>
      )}
    </div>
  );
}
