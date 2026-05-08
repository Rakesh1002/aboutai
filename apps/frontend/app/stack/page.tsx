import { getStack } from "@/lib/content";
import { NewsletterSignup } from "@/components/newsletter-signup";

export const metadata = {
  title: "Stack Mirror",
  description:
    "The AI tools every startup in the 30-stack portfolio is currently running in production. Updated monthly.",
};

const STATUS_STYLE: Record<string, string> = {
  "in-production":
    "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  trialing:
    "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  "ripped-out":
    "bg-zinc-200 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 line-through",
};

export default function StackPage() {
  const stack = getStack();

  return (
    <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
      <header className="mb-10 border-b border-zinc-200 pb-8 dark:border-zinc-800">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-4xl">
          Stack Mirror
        </h1>
        <p className="mt-3 max-w-2xl text-zinc-600 dark:text-zinc-400">
          Every AI tool currently running in production across the 30
          startups in the portfolio. Updated monthly. The diff is the most
          honest signal of what works.
        </p>
        <p className="mt-4 text-xs text-zinc-500">
          Public JSON feed:{" "}
          <a
            href="/stack.json"
            className="font-mono underline hover:text-zinc-900 dark:hover:text-zinc-100"
          >
            /stack.json
          </a>
        </p>
      </header>

      {stack.length === 0 ? (
        <div className="rounded-xl border border-dashed border-zinc-300 bg-zinc-50 p-10 text-center dark:border-zinc-700 dark:bg-zinc-900">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Stack Mirror v0 ships July 1, 2026.
          </p>
        </div>
      ) : (
        <div className="space-y-12">
          {stack.map((startup) => (
            <section
              key={startup.slug}
              className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900"
            >
              <div className="flex items-baseline justify-between gap-4">
                <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
                  {startup.url ? (
                    <a
                      href={startup.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:underline"
                    >
                      {startup.name}
                    </a>
                  ) : (
                    startup.name
                  )}
                </h2>
                <span className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                  {startup.stage}
                </span>
              </div>

              <ul className="mt-4 divide-y divide-zinc-100 dark:divide-zinc-800">
                {startup.tools.map((tool) => (
                  <li
                    key={`${startup.slug}-${tool.vendor}-${tool.category}`}
                    className="flex flex-wrap items-center gap-3 py-3 text-sm"
                  >
                    <span className="w-32 shrink-0 font-mono text-xs uppercase tracking-wider text-zinc-500">
                      {tool.category}
                    </span>
                    <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                      {tool.vendor}
                    </span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLE[tool.status] ?? ""}`}
                    >
                      {tool.status}
                    </span>
                    {tool.monthlyCostUsd !== undefined && (
                      <span className="font-mono text-xs text-zinc-500">
                        ${tool.monthlyCostUsd}/mo
                      </span>
                    )}
                    {tool.notes && (
                      <span className="basis-full pl-32 text-xs text-zinc-600 dark:text-zinc-400">
                        {tool.notes}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}

      <div className="mt-16 border-t border-zinc-200 pt-10 dark:border-zinc-800">
        <NewsletterSignup variant="card" source="stack" />
      </div>
    </div>
  );
}
