import Link from "next/link";

export const metadata = {
  title: "Confirmed",
  robots: { index: false },
};

const COPY = {
  ok: {
    title: "You're confirmed.",
    body: "You'll get the first teardown Friday May 22, 2026 — IST morning. Until then, the live Stack Mirror has every AI tool currently running across the portfolio.",
  },
  already: {
    title: "Already confirmed.",
    body: "You're on the list — no action needed. First teardown drops Friday May 22, 2026.",
  },
  expired: {
    title: "Confirmation link expired.",
    body: "That link expired (links are valid for 7 days). Subscribe again from the homepage and you'll get a fresh one.",
  },
  invalid: {
    title: "That link doesn't look right.",
    body: "It might have been used already, mistyped, or just timed out. Subscribe again from the homepage for a new confirmation email.",
  },
} as const;

type Status = keyof typeof COPY;

function pickStatus(raw: string | string[] | undefined): Status {
  const v = Array.isArray(raw) ? raw[0] : raw;
  if (v && v in COPY) return v as Status;
  return "ok";
}

export default async function ConfirmedPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string }>;
}) {
  const params = await searchParams;
  const status = pickStatus(params.status);
  const c = COPY[status];

  return (
    <div className="mx-auto max-w-xl px-4 py-24 text-center sm:px-6">
      <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-4xl">
        {c.title}
      </h1>
      <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">{c.body}</p>
      <div className="mt-10 flex justify-center gap-3">
        <Link
          href="/stack"
          className="inline-flex h-10 items-center justify-center rounded-md border border-zinc-200 px-4 text-sm font-medium text-zinc-900 hover:bg-zinc-100 dark:border-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-800"
        >
          See the Stack Mirror
        </Link>
        <Link
          href="/"
          className="inline-flex h-10 items-center justify-center rounded-md bg-zinc-900 px-4 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-100"
        >
          Home
        </Link>
      </div>
    </div>
  );
}
