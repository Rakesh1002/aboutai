import Link from "next/link";

export const metadata = {
  title: "Unsubscribed",
  robots: { index: false },
};

const COPY = {
  ok: {
    title: "Unsubscribed.",
    body: "You're off the list. No follow-up sequence, no \"are you sure\" emails — that's the whole point.",
  },
  already: {
    title: "Already unsubscribed.",
    body: "You were already off the list. Nothing more to do.",
  },
  invalid: {
    title: "That link doesn't look right.",
    body: "It might be malformed or already used. If you're still receiving emails, reply to any one and Rakesh will remove you manually.",
  },
} as const;

type Status = keyof typeof COPY;

function pickStatus(raw: string | string[] | undefined): Status {
  const v = Array.isArray(raw) ? raw[0] : raw;
  if (v && v in COPY) return v as Status;
  return "ok";
}

export default async function UnsubscribedPage({
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
      <div className="mt-10">
        <Link
          href="/"
          className="inline-flex h-10 items-center justify-center rounded-md border border-zinc-200 px-4 text-sm font-medium text-zinc-900 hover:bg-zinc-100 dark:border-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-800"
        >
          Home
        </Link>
      </div>
    </div>
  );
}
