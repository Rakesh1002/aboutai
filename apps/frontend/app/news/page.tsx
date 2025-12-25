import { Metadata } from "next";
import { getAllNewsAsync, getAllVerticals } from "@/lib/content";
import { NewsCard, NewsGrid } from "@/components/news/news-card";
import { Button } from "@/components/ui/button";

export const metadata: Metadata = {
  title: "AI News & Intelligence",
  description:
    "Stay informed with verified AI news. Our Hype Meter cuts through the noise. Vertical-specific coverage for professionals.",
};

// Revalidate every 60 seconds for fresh content
export const revalidate = 60;

export default async function NewsPage() {
  const articles = await getAllNewsAsync();
  const verticals = getAllVerticals();
  const featuredArticle = articles[0];
  const otherArticles = articles.slice(1);

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
          AI News & Intelligence
        </h1>
        <p className="mt-2 text-lg text-zinc-600 dark:text-zinc-400">
          Cut through the hype. Every story scored for sensationalism.
        </p>
      </div>

      {/* Vertical Filters */}
      <div className="mb-8 flex flex-wrap gap-2 border-b border-zinc-200 pb-6 dark:border-zinc-800">
        <Button variant="secondary" size="sm">
          All
        </Button>
        {verticals.map((vertical) => (
          <Button key={vertical} variant="outline" size="sm">
            {vertical.charAt(0).toUpperCase() + vertical.slice(1)}
          </Button>
        ))}
      </div>

      {/* Featured Article */}
      {featuredArticle && (
        <div className="mb-12">
          <h2 className="mb-4 text-sm font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Featured
          </h2>
          <NewsCard article={featuredArticle} featured />
        </div>
      )}

      {/* Other Articles */}
      {otherArticles.length > 0 && (
        <div>
          <h2 className="mb-4 text-sm font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Latest
          </h2>
          <NewsGrid articles={otherArticles} />
        </div>
      )}

      {/* Empty state */}
      {articles.length === 0 && (
        <div className="py-12 text-center">
          <p className="text-lg text-zinc-600 dark:text-zinc-400">
            No articles yet. Check back soon!
          </p>
          <p className="mt-2 text-sm text-zinc-500">
            Our editorial team is working on investigative pieces.
          </p>
        </div>
      )}

      {/* Newsletter CTA */}
      <div className="mt-16 rounded-2xl bg-zinc-100 p-8 text-center dark:bg-zinc-900">
        <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
          Don&apos;t miss a story
        </h3>
        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
          Get our weekly digest delivered to your inbox. No hype, just verified
          insights.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <input
            type="email"
            placeholder="you@company.com"
            className="w-full max-w-xs rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm dark:border-zinc-800 dark:bg-zinc-950"
          />
          <Button>Subscribe</Button>
        </div>
      </div>
    </div>
  );
}

