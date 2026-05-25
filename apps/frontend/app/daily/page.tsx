import Link from "next/link";
import type { Metadata } from "next";
import { getAllDailies } from "@/lib/content";
import { NewsletterSignup } from "@/components/newsletter-signup";
import { formatDate } from "@/lib/utils";

export const metadata: Metadata = {
  title: "Daily — 5 minutes of AI for Indian builders",
  description:
    "Mon–Thu at 7am IST. Five things that landed yesterday and what each one means for an Indian builder shipping AI in production this week.",
};

export default function DailyIndexPage() {
  const dailies = getAllDailies();

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <header className="mb-12 border-b border-zinc-200 pb-8 dark:border-zinc-800">
        <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
          Daily
        </p>
        <h1 className="mt-2 text-balance text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-4xl">
          5 minutes of AI for Indian builders.
        </h1>
        <p className="mt-4 text-zinc-600 dark:text-zinc-400">
          Mon–Thu at 7am IST. Five things that landed yesterday and what each
          one means for an Indian builder shipping AI in production this week.
          Friday is the long teardown.
        </p>
        <div className="mt-8 max-w-md">
          <NewsletterSignup variant="minimal" source="daily-index" />
          <p className="mt-3 text-xs text-zinc-500">
            Free. One email each weekday. Unsubscribe in one click.
          </p>
        </div>
      </header>

      {dailies.length === 0 ? (
        <div className="rounded-xl border border-dashed border-zinc-300 bg-zinc-50 p-8 dark:border-zinc-700 dark:bg-zinc-900">
          <p className="font-medium text-zinc-900 dark:text-zinc-100">
            No public dailies yet.
          </p>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
            The public launch is blocked until 4 daily issues and 2 Friday
            teardowns are banked, and the email loop has been verified
            end-to-end.
          </p>
        </div>
      ) : (
        <ul className="divide-y divide-zinc-200 dark:divide-zinc-800">
          {dailies.map((daily) => (
            <li key={daily.date} className="py-6">
              <Link
                href={`/daily/${daily.date}`}
                className="group block"
              >
                <div className="flex items-baseline gap-4">
                  <time
                    dateTime={daily.date}
                    className="w-24 shrink-0 font-mono text-xs text-zinc-500"
                  >
                    {formatDate(daily.date)}
                  </time>
                  <div>
                    <p className="font-semibold text-zinc-900 group-hover:underline dark:text-zinc-100">
                      {daily.title}
                    </p>
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                      {daily.intro}
                    </p>
                    <p className="mt-2 text-xs text-zinc-500">
                      {daily.stories.length} stories ·{" "}
                      {daily.stories.filter((s) => s.importance === "must-read").length}{" "}
                      must-read
                    </p>
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
