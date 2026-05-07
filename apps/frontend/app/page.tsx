import Link from "next/link";
import { NewsletterSignup } from "@/components/newsletter-signup";
import { getAllEssays } from "@/lib/content";

const UPCOMING = [
  {
    week: "May 22",
    title: "What we ripped out of 30 startups in Q1 2026",
    note: "Every AI tool I tried and dropped across the portfolio in Jan–Mar. Why each one left.",
  },
  {
    week: "May 29",
    title: "Workers AI vs OpenAI vs Groq — three months of bills",
    note: "Real invoices, redacted org names. P50/P99 latency at $X/month and Y QPS. The cost surprise nobody warned me about.",
  },
  {
    week: "Jun 5",
    title: "Six AI sales-agent tools, my real inbox, one week",
    note: "Forensic, screenshot-heavy, names named. Two of six were silently using GPT-3.5.",
  },
  {
    week: "Jun 12",
    title: "Razorpay + Stripe + Cashfree for Indian SaaS in 2026",
    note: "Which actually plays nice with India-first billing. UPI auto-debit reality check.",
  },
];

export default function HomePage() {
  const essays = getAllEssays();

  return (
    <div className="flex flex-col">
      <section className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="mx-auto max-w-3xl px-4 py-20 sm:px-6 lg:py-28">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white px-3 py-1 text-xs font-medium text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
            Launches Friday May 22, 2026
          </div>

          <h1 className="text-balance text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-5xl">
            30 production AI stacks.
            <br />
            One honest teardown a week.
          </h1>

          <p className="mt-6 text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
            I run 30 AI-native startups. I pay for the tools, I rip them out
            when they break, and every Friday I publish what I learned —
            screenshots, configs, latency numbers, billing line items, and a
            three-state verdict.{" "}
            <span className="font-medium text-zinc-900 dark:text-zinc-100">
              No affiliates, no hype, no sponsored conclusions.
            </span>
          </p>

          <div className="mt-10">
            <NewsletterSignup variant="minimal" />
            <p className="mt-3 text-xs text-zinc-500">
              Free. One email Friday morning IST. Unsubscribe in one click.
            </p>
          </div>
        </div>
      </section>

      <section className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
            What you&apos;ll read in the first 4 weeks
          </h2>
          <ul className="mt-6 divide-y divide-zinc-200 dark:divide-zinc-800">
            {UPCOMING.map((item) => (
              <li key={item.week} className="py-5">
                <div className="flex items-baseline gap-4">
                  <div className="w-16 shrink-0 font-mono text-xs text-zinc-500">
                    {item.week}
                  </div>
                  <div>
                    <p className="font-semibold text-zinc-900 dark:text-zinc-100">
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
              Latest teardowns
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
                        ? new Intl.DateTimeFormat("en-US", {
                            month: "short",
                            day: "numeric",
                          }).format(new Date(essay.publishedAt))
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
            Get the first teardown Friday morning.
          </h2>
          <div className="mx-auto mt-8 max-w-md">
            <NewsletterSignup variant="minimal" />
          </div>
        </div>
      </section>
    </div>
  );
}
