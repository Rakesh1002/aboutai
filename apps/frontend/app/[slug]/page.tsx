import { notFound } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";
import { compileMDX } from "next-mdx-remote/rsc";
import { getEssayBySlug, getEssaySlugs } from "@/lib/content";
import { gateEssay, type Visitor } from "@/lib/paywall";
import { readSession, SESSION_COOKIE_NAME } from "@/lib/session";
import { getEnv } from "@/lib/cf";
import { InlineEmailGate } from "@/components/inline-email-gate";
import { PaywallCard } from "@/components/paywall-card";
import { NewsletterSignup } from "@/components/newsletter-signup";
import { formatDate } from "@/lib/utils";
import type { Metadata } from "next";

export async function generateStaticParams() {
  return getEssaySlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const essay = getEssayBySlug(slug);
  if (!essay) return {};
  return {
    title: essay.title,
    description: essay.excerpt,
    openGraph: {
      title: essay.title,
      description: essay.excerpt,
      type: "article",
      publishedTime: essay.publishedAt,
    },
  };
}

const VERDICT_LABEL: Record<string, { label: string; cls: string }> = {
  "ship-it": {
    label: "Ship it",
    cls: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  },
  "trial-only": {
    label: "Trial only",
    cls: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  },
  avoid: {
    label: "Avoid",
    cls: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  },
};

async function resolveVisitor(): Promise<Visitor> {
  try {
    const env = getEnv();
    const secret = env.SESSION_SECRET;
    if (!secret) return "anon";
    const c = await cookies();
    const raw = c.get(SESSION_COOKIE_NAME)?.value;
    const session = await readSession(raw, secret);
    return session ? session.tier : "anon";
  } catch {
    return "anon";
  }
}

export default async function EssayPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const essay = getEssayBySlug(slug);
  if (!essay) notFound();

  const visitor = await resolveVisitor();
  const gated = gateEssay(essay, visitor);

  const { content: visibleContent } = await compileMDX({
    source: gated.visible,
    options: { parseFrontmatter: false },
  });

  const verdict = essay.verdict ? VERDICT_LABEL[essay.verdict] : null;

  return (
    <article className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
      <header className="mb-10 border-b border-zinc-200 pb-8 dark:border-zinc-800">
        <Link
          href="/archive"
          className="text-xs font-medium text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
        >
          ← Archive
        </Link>
        <h1 className="mt-4 text-balance text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-4xl">
          {essay.title}
        </h1>
        <div className="mt-4 flex flex-wrap items-center gap-3 text-sm text-zinc-500">
          {essay.publishedAt && (
            <time dateTime={essay.publishedAt}>
              {formatDate(essay.publishedAt)}
            </time>
          )}
          {verdict && (
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${verdict.cls}`}
            >
              {verdict.label}
            </span>
          )}
          {essay.paywall === "paid" && (
            <span className="rounded-full bg-zinc-900 px-2.5 py-0.5 text-xs font-medium text-white dark:bg-zinc-100 dark:text-zinc-900">
              Members only
            </span>
          )}
        </div>
        <p className="mt-4 text-xs text-zinc-500">
          Written by Rakesh Roushan in Bangalore — running 30 AI-native
          startups, profitable on AudioPod, opinionated about everything else.
        </p>
        {essay.excerpt && (
          <p className="mt-6 text-lg text-zinc-600 dark:text-zinc-400">
            {essay.excerpt}
          </p>
        )}
      </header>

      <div className="prose prose-zinc max-w-none prose-headings:font-bold prose-a:underline dark:prose-invert">
        {visibleContent}
      </div>

      {gated.state === "email-gate" && (
        <InlineEmailGate source="inline-gate" essaySlug={slug} />
      )}

      {gated.state === "paywall" && (
        <PaywallCard essaySlug={slug} />
      )}

      {gated.state === "open" && (
        <div className="mt-16 border-t border-zinc-200 pt-10 dark:border-zinc-800">
          <NewsletterSignup variant="card" source={`essay:${slug}`} />
        </div>
      )}
    </article>
  );
}
