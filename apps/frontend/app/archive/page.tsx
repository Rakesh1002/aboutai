import Link from "next/link";
import { getAllEssays } from "@/lib/content";
import { formatShortDate } from "@/lib/utils";
import { NewsletterSignup } from "@/components/newsletter-signup";

export const metadata = {
  title: "Archive",
  description: "Every teardown, in order.",
};

export default function ArchivePage() {
  const essays = getAllEssays();

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <header className="mb-10 border-b border-zinc-200 pb-8 dark:border-zinc-800">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-4xl">
          Archive
        </h1>
        <p className="mt-3 text-zinc-600 dark:text-zinc-400">
          Every teardown, in order. The latest 12 weeks are free; older issues
          require membership once the paid tier opens.
        </p>
      </header>

      {essays.length === 0 ? (
        <div className="rounded-xl border border-dashed border-zinc-300 bg-zinc-50 p-10 text-center dark:border-zinc-700 dark:bg-zinc-900">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            First teardown drops Friday May 22, 2026.
          </p>
          <div className="mx-auto mt-6 max-w-md">
            <NewsletterSignup variant="minimal" source="archive-empty" />
          </div>
        </div>
      ) : (
        <ul className="divide-y divide-zinc-200 dark:divide-zinc-800">
          {essays.map((essay) => (
            <li key={essay.slug} className="py-5">
              <Link
                href={`/${essay.slug}`}
                className="group flex items-baseline gap-4"
              >
                <div className="w-16 shrink-0 font-mono text-xs text-zinc-500">
                  {essay.publishedAt
                    ? formatShortDate(essay.publishedAt)
                    : "Draft"}
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-zinc-900 group-hover:underline dark:text-zinc-100">
                    {essay.title}
                  </p>
                  {essay.excerpt && (
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                      {essay.excerpt}
                    </p>
                  )}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
