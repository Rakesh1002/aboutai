"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type SubscribeStatus = "idle" | "loading" | "success" | "error";

interface NewsletterSignupProps {
  variant?: "default" | "minimal" | "card";
  className?: string;
}

export function NewsletterSignup({
  variant = "default",
  className = "",
}: NewsletterSignupProps) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<SubscribeStatus>("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setStatus("loading");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/newsletter/subscribe`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, source: "website" }),
        }
      );

      if (response.ok) {
        setStatus("success");
        setEmail("");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  if (status === "success") {
    return (
      <div className={`text-center ${className}`}>
        <div className="inline-flex items-center gap-2 rounded-full bg-emerald-100 dark:bg-emerald-900/30 px-4 py-2 text-sm font-medium text-emerald-700 dark:text-emerald-400">
          <span>✓</span>
          <span>Welcome aboard! Check your inbox.</span>
        </div>
      </div>
    );
  }

  if (variant === "minimal") {
    return (
      <form onSubmit={handleSubmit} className={`flex gap-2 ${className}`}>
        <Input
          type="email"
          placeholder="you@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="flex-1"
        />
        <Button type="submit" isLoading={status === "loading"}>
          Subscribe
        </Button>
      </form>
    );
  }

  if (variant === "card") {
    return (
      <div
        className={`rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-6 ${className}`}
        id="newsletter"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-lg">
            📬
          </div>
          <div>
            <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
              Weekly AI Digest
            </h3>
            <p className="text-sm text-zinc-500">No spam, unsubscribe anytime</p>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            type="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="flex-1"
          />
          <Button type="submit" isLoading={status === "loading"}>
            Join
          </Button>
        </form>
        {status === "error" && (
          <p className="mt-2 text-xs text-red-500">
            Something went wrong. Please try again.
          </p>
        )}
      </div>
    );
  }

  // Default variant
  return (
    <div className={className} id="newsletter">
      <form onSubmit={handleSubmit} className="flex gap-3 max-w-md mx-auto">
        <Input
          type="email"
          placeholder="you@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="flex-1"
        />
        <Button type="submit" isLoading={status === "loading"}>
          {status === "loading" ? "..." : "Subscribe"}
        </Button>
      </form>
      {status === "error" && (
        <p className="mt-2 text-center text-xs text-red-500">
          Something went wrong. Please try again.
        </p>
      )}
    </div>
  );
}

