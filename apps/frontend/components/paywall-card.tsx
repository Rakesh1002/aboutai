"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface PaywallCardProps {
  essaySlug: string;
  monthlyPriceUsd?: number;
  yearlyPriceUsd?: number;
}

export function PaywallCard({
  essaySlug,
  monthlyPriceUsd = 25,
  yearlyPriceUsd = 240,
}: PaywallCardProps) {
  const [email, setEmail] = useState("");
  const [emailStatus, setEmailStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [checkoutLoading, setCheckoutLoading] = useState<
    "monthly" | "yearly" | null
  >(null);
  const router = useRouter();

  const submitEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setEmailStatus("loading");
    setErrorMsg(null);
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          source: `paywall:${essaySlug}`,
        }),
      });
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as {
          error?: string;
        };
        setErrorMsg(data.error ?? "Subscription failed.");
        setEmailStatus("error");
        return;
      }
      setEmailStatus("success");
      setEmail("");
      router.refresh();
    } catch {
      setErrorMsg("Network error. Try again.");
      setEmailStatus("error");
    }
  };

  const startCheckout = async (plan: "monthly" | "yearly") => {
    setCheckoutLoading(plan);
    try {
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan, returnTo: `/${essaySlug}` }),
      });
      if (!res.ok) {
        setCheckoutLoading(null);
        setErrorMsg(
          "Checkout isn't open yet — drop your email below for free teardowns until it is."
        );
        return;
      }
      const data = (await res.json()) as { url?: string };
      if (data.url) {
        window.location.href = data.url;
      } else {
        setCheckoutLoading(null);
      }
    } catch {
      setCheckoutLoading(null);
      setErrorMsg("Couldn't reach checkout. Try the email option below.");
    }
  };

  return (
    <div
      role="region"
      aria-label="Subscribe to read the rest"
      className="my-10 rounded-xl border-2 border-zinc-900 bg-white p-6 dark:border-zinc-100 dark:bg-zinc-950"
    >
      <p className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
        Members only
      </p>
      <h3 className="mt-2 text-xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
        The methodology, the configs, and the receipts.
      </h3>
      <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        Get the full archive plus deep-dive teardowns for paying members.
      </p>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => startCheckout("monthly")}
          disabled={checkoutLoading !== null}
          className="rounded-lg border border-zinc-200 bg-white p-4 text-left transition-colors hover:border-zinc-400 disabled:opacity-50 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-600"
        >
          <p className="text-sm text-zinc-500">Monthly</p>
          <p className="mt-1 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            ${monthlyPriceUsd}
            <span className="text-sm font-normal text-zinc-500"> / mo</span>
          </p>
          <p className="mt-2 text-xs text-zinc-500">
            {checkoutLoading === "monthly" ? "Loading…" : "Start now →"}
          </p>
        </button>
        <button
          type="button"
          onClick={() => startCheckout("yearly")}
          disabled={checkoutLoading !== null}
          className="rounded-lg border-2 border-zinc-900 bg-white p-4 text-left transition-colors hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-100 dark:bg-zinc-900 dark:hover:bg-zinc-800"
        >
          <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
            Yearly · save 20%
          </p>
          <p className="mt-1 text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            ${yearlyPriceUsd}
            <span className="text-sm font-normal text-zinc-500"> / yr</span>
          </p>
          <p className="mt-2 text-xs text-zinc-500">
            {checkoutLoading === "yearly" ? "Loading…" : "Start now →"}
          </p>
        </button>
      </div>

      <div className="mt-8 border-t border-zinc-200 pt-6 dark:border-zinc-800">
        <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
          Not ready to pay?
        </p>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          Drop your email — I&apos;ll send you free teardowns every Friday.
          Subscribe when you&apos;re ready.
        </p>
        {emailStatus === "success" ? (
          <div className="mt-4 inline-flex items-center gap-2 rounded-md bg-emerald-100 px-3 py-1.5 text-sm font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
            <span aria-hidden>✓</span>
            <span>Confirmation sent — check your inbox.</span>
          </div>
        ) : (
          <form
            onSubmit={submitEmail}
            className="mt-4 flex flex-col gap-2 sm:flex-row"
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
            <Button type="submit" isLoading={emailStatus === "loading"}>
              Send free ones
            </Button>
          </form>
        )}
        {errorMsg && <p className="mt-2 text-xs text-red-500">{errorMsg}</p>}
      </div>
    </div>
  );
}
