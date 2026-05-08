import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { getAllDailies, getDailyByDate, getDailyDates } from "@/lib/content";
import type { DailyStory, StoryImportance } from "@/lib/content";
import { InlineSponsor } from "@/components/inline-sponsor";
import { NewsletterSignup } from "@/components/newsletter-signup";
import { formatDate } from "@/lib/utils";

export async function generateStaticParams() {
  return getDailyDates().map((date) => ({ date }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ date: string }>;
}): Promise<Metadata> {
  const { date } = await params;
  const daily = getDailyByDate(date);
  if (!daily) return {};
  return {
    title: daily.title,
    description: daily.intro,
    openGraph: {
      title: daily.title,
      description: daily.intro,
      type: "article",
      publishedTime: daily.date,
    },
  };
}

const IMPORTANCE_LABEL: Record<StoryImportance, { label: string; cls: string }> = {
  "must-read": {
    label: "Must read",
    cls: "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900",
  },
  notable: {
    label: "Notable",
    cls: "bg-zinc-200 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
  },
  fyi: {
    label: "FYI",
    cls: "bg-transparent text-zinc-500 dark:text-zinc-500",
  },
};

function StoryCard({ story, index }: { story: DailyStory; index: number }) {
  const tag = IMPORTANCE_LABEL[story.importance];
  return (
    <article className="border-t border-zinc-200 py-8 dark:border-zinc-800">
      <div className="flex items-start gap-4">
        <span className="mt-1 w-6 shrink-0 font-mono text-sm text-zinc-400">
          {String(index + 1).padStart(2, "0")}
        </span>
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
            <span
              className={`rounded-full px-2 py-0.5 font-medium ${tag.cls}`}
            >
              {tag.label}
            </span>
            <span className="font-mono uppercase tracking-wider text-zinc-500">
              {story.source}
            </span>
          </div>
          <h2 className="text-balance text-lg font-semibold leading-snug text-zinc-900 dark:text-zinc-100">
            <a
              href={story.link}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
            >
              {story.headline}
            </a>
          </h2>
          <p className="mt-3 leading-relaxed text-zinc-700 dark:text-zinc-300">
            {story.summary}
          </p>
          <p className="mt-3 border-l-2 border-zinc-900 pl-4 text-sm leading-relaxed text-zinc-700 dark:border-zinc-100 dark:text-zinc-300">
            <span className="font-semibold text-zinc-900 dark:text-zinc-100">
              For Indian builders:
            </span>{" "}
            {story.indiaTakeaway}
          </p>
        </div>
      </div>
    </article>
  );
}

export default async function DailyReaderPage({
  params,
}: {
  params: Promise<{ date: string }>;
}) {
  const { date } = await params;
  const daily = getDailyByDate(date);
  if (!daily) notFound();

  const all = getAllDailies();
  const idx = all.findIndex((d) => d.date === daily.date);
  const newer = idx > 0 ? all[idx - 1] : null;
  const older = idx >= 0 && idx < all.length - 1 ? all[idx + 1] : null;

  // Show inline sponsor after story #2 (or end if fewer stories).
  const sponsorAfterIndex = Math.min(1, daily.stories.length - 1);

  return (
    <article className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
      <header className="mb-10">
        <Link
          href="/daily"
          className="text-xs font-medium text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
        >
          ← All dailies
        </Link>
        <p className="mt-4 font-mono text-xs uppercase tracking-wider text-zinc-500">
          {formatDate(daily.date)} · Daily
        </p>
        <h1 className="mt-2 text-balance text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-4xl">
          {daily.title}
        </h1>
        <p className="mt-6 text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
          {daily.intro}
        </p>
      </header>

      <div>
        {daily.stories.map((story, i) => (
          <div key={story.link}>
            <StoryCard story={story} index={i} />
            {i === sponsorAfterIndex && daily.sponsor && (
              <InlineSponsor sponsorId={daily.sponsor.sponsorId} />
            )}
          </div>
        ))}
      </div>

      {daily.outro && (
        <p className="mt-12 border-t border-zinc-200 pt-8 leading-relaxed text-zinc-700 dark:border-zinc-800 dark:text-zinc-300">
          {daily.outro}
        </p>
      )}

      <div className="mt-16 border-t border-zinc-200 pt-10 dark:border-zinc-800">
        <NewsletterSignup variant="card" source={`daily:${daily.date}`} />
      </div>

      <nav className="mt-12 flex justify-between border-t border-zinc-200 pt-6 text-sm dark:border-zinc-800">
        {older ? (
          <Link
            href={`/daily/${older.date}`}
            className="text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
          >
            ← {formatDate(older.date)}
          </Link>
        ) : (
          <span />
        )}
        {newer ? (
          <Link
            href={`/daily/${newer.date}`}
            className="text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
          >
            {formatDate(newer.date)} →
          </Link>
        ) : (
          <span />
        )}
      </nav>
    </article>
  );
}
