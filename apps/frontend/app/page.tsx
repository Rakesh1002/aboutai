import Link from "next/link";
import { NewsletterSignup } from "@/components/newsletter-signup";
import { getAllDailies, getAllEssays } from "@/lib/content";
import { formatShortDate } from "@/lib/utils";

const UPCOMING = [
  {
    when: "Gate 1",
    kind: "Content bank",
    title: "4 daily issues banked",
    note: "No public send until four dated rundowns are written, sourced, human-edited, and ready to publish.",
  },
  {
    when: "Gate 2",
    kind: "Teardowns",
    title: "2 operator-seat teardowns banked",
    note: "The wedge is production receipts from 30 stacks. Generic daily news does not launch without this proof.",
  },
  {
    when: "Gate 3",
    kind: "Delivery",
    title: "Signup, confirm, unsubscribe, and test broadcast verified",
    note: "The list must prove the full email loop before any public launch tweet goes out.",
  },
  {
    when: "30 days",
    kind: "Validation",
    title: "12+ dailies, 4 teardowns, 500–1,000 subscribers",
    note: "Continue only if the sprint shows 40%+ open rate and one real sponsor conversation or paid pilot.",
  },
  {
    when: "Decision",
    kind: "Go / no-go",
    title: "Continue only if operator-seat content pulls",
    note: "If the most-shared work is generic news, fold this into AudioPod content marketing.",
  },
];

export default function HomePage() {
  const dailies = getAllDailies();
  const essays = getAllEssays();
  const latestDaily = dailies[0] ?? null;

  return (
    <div className="flex flex-col">
      <section className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="mx-auto max-w-3xl px-4 py-20 sm:px-6 lg:py-28">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white px-3 py-1 text-xs font-medium text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
            Validation list open · public launch gated
          </div>

          <h1 className="text-balance text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-5xl">
            5 minutes of AI for Indian builders, daily.
            <br />
            Plus weekly teardowns from 30 production stacks.
          </h1>

          <p className="mt-6 text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
            The public launch is intentionally gated. Mon–Thu will be five
            things that landed yesterday and what each one means for an Indian
            builder shipping AI in production this week. Friday will be a
            long-form teardown of one tool I&apos;m actually
            paying for across 30 stacks — screenshots, configs, latency
            numbers, billing line items, verdict.{" "}
            <span className="font-medium text-zinc-900 dark:text-zinc-100">
              No affiliates, no hype, no sponsored conclusions.
            </span>
          </p>

          <div className="mt-10">
            <NewsletterSignup variant="minimal" />
            <p className="mt-3 text-xs text-zinc-500">
              Free validation list. Public send starts only after the readiness
              gates pass. Unsubscribe in one click.
            </p>
          </div>
        </div>
      </section>

      {latestDaily && (
        <section className="border-b border-zinc-200 dark:border-zinc-800">
          <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
              Today&apos;s daily
            </h2>
            <Link
              href={`/daily/${latestDaily.date}`}
              className="group mt-6 block rounded-2xl border border-zinc-200 bg-white p-6 transition-colors hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-700"
            >
              <p className="font-mono text-xs uppercase tracking-wider text-zinc-500">
                {formatShortDate(latestDaily.date)} ·{" "}
                {latestDaily.stories.length} stories
              </p>
              <p className="mt-2 text-xl font-semibold text-zinc-900 group-hover:underline dark:text-zinc-100">
                {latestDaily.title}
              </p>
              <p className="mt-3 text-zinc-600 dark:text-zinc-400">
                {latestDaily.intro}
              </p>
              <p className="mt-4 text-sm font-medium text-zinc-900 group-hover:underline dark:text-zinc-100">
                Read today&apos;s daily →
              </p>
            </Link>
            {dailies.length > 1 && (
              <p className="mt-4 text-sm">
                <Link
                  href="/daily"
                  className="text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
                >
                  All {dailies.length} dailies →
                </Link>
              </p>
            )}
          </div>
        </section>
      )}

      <section className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
            What has to be true before public launch
          </h2>
          <ul className="mt-6 divide-y divide-zinc-200 dark:divide-zinc-800">
            {UPCOMING.map((item) => (
              <li key={item.when} className="py-5">
                <div className="flex items-baseline gap-4">
                  <div className="w-24 shrink-0 font-mono text-xs text-zinc-500">
                    {item.when}
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                      {item.kind}
                    </p>
                    <p className="mt-1 font-semibold text-zinc-900 dark:text-zinc-100">
                      {item.title}
                    </p>
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                      {item.note}
                    </p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {essays.length > 0 && (
        <section className="border-b border-zinc-200 dark:border-zinc-800">
          <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
              Latest Friday teardowns
            </h2>
            <ul className="mt-6 divide-y divide-zinc-200 dark:divide-zinc-800">
              {essays.slice(0, 5).map((essay) => (
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
                    <div>
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
          </div>
        </section>
      )}

      <section className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
            Who writes this
          </h2>
          <div className="mt-4 space-y-4 text-zinc-700 dark:text-zinc-300">
            <p>
              I&apos;m Rakesh Roushan. I run a portfolio of 30 AI-native
              startups out of Bangalore — most pre-PMF, one (
              <a
                href="https://audiopod.ai"
                className="underline hover:text-zinc-900 dark:hover:text-zinc-100"
              >
                AudioPod
              </a>
              ) profitable in 100+ countries.
            </p>
            <p>
              That means I&apos;m paying for, integrating, and ripping out AI
              tools every week — in production, with real customer money on the
              line. Most reviews you read on the internet were written by
              someone who tried the tool for an afternoon. Mine are written by
              someone who shipped it for three weeks.
            </p>
            <p className="font-medium text-zinc-900 dark:text-zinc-100">
              I&apos;m not selling anything except this newsletter.
            </p>
          </div>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6">
          <h2 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
            Join the validation list.
          </h2>
          <div className="mx-auto mt-8 max-w-md">
            <NewsletterSignup variant="minimal" />
          </div>
        </div>
      </section>
    </div>
  );
}
