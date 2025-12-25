"use client";

import Link from "next/link";
import Image from "next/image";
import { Card } from "@/components/ui/card";
import { cn, formatDate } from "@/lib/utils";
import type { NewsArticle } from "@/lib/content";

interface NewsCardProps {
  article: NewsArticle;
  featured?: boolean;
  className?: string;
}

export function NewsCard({
  article,
  featured = false,
  className,
}: NewsCardProps) {
  if (featured) {
    return (
      <Link href={`/news/${article.slug}`}>
        <Card hover className={cn("group overflow-hidden", className)}>
          <div className="grid md:grid-cols-2">
            {/* Image */}
            <div className="relative aspect-[16/9] md:aspect-auto">
              {article.coverImage ? (
                <Image
                  src={article.coverImage}
                  alt={article.title}
                  fill
                  className="object-cover transition-transform group-hover:scale-105"
                />
              ) : (
                <div className="flex h-full min-h-[200px] items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600">
                  <span className="text-4xl">📰</span>
                </div>
              )}
            </div>

            {/* Content */}
            <div className="flex flex-col justify-center p-6">
              <div className="flex items-center gap-2 text-sm text-zinc-500 dark:text-zinc-400">
                {article.vertical && (
                  <>
                    <span className="font-medium capitalize text-indigo-600 dark:text-indigo-400">
                      {article.vertical}
                    </span>
                    <span>·</span>
                  </>
                )}
                <time dateTime={article.publishedAt}>
                  {formatDate(article.publishedAt)}
                </time>
              </div>

              <h2 className="mt-2 text-2xl font-bold text-zinc-900 group-hover:text-indigo-600 dark:text-zinc-100 dark:group-hover:text-indigo-400">
                {article.title}
              </h2>

              <p className="mt-3 line-clamp-3 text-zinc-600 dark:text-zinc-400">
                {article.excerpt}
              </p>

              <div className="mt-4 flex items-center gap-2 text-sm">
                <span className="text-zinc-900 dark:text-zinc-100">
                  {article.author}
                </span>
                {article.hypeScore !== undefined && (
                  <>
                    <span className="text-zinc-300 dark:text-zinc-700">·</span>
                    <span
                      className={cn(
                        "font-medium",
                        article.hypeScore <= 30
                          ? "text-emerald-600"
                          : article.hypeScore <= 60
                            ? "text-amber-600"
                            : "text-red-600"
                      )}
                    >
                      Hype: {article.hypeScore}%
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>
        </Card>
      </Link>
    );
  }

  return (
    <Link href={`/news/${article.slug}`}>
      <Card hover className={cn("group h-full overflow-hidden", className)}>
        {/* Image */}
        <div className="relative aspect-[16/9]">
          {article.coverImage ? (
            <Image
              src={article.coverImage}
              alt={article.title}
              fill
              className="object-cover transition-transform group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full items-center justify-center bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-800 dark:to-zinc-900">
              <span className="text-3xl">📰</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-5">
          <div className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
            {article.vertical && (
              <>
                <span className="font-medium capitalize text-indigo-600 dark:text-indigo-400">
                  {article.vertical}
                </span>
                <span>·</span>
              </>
            )}
            <time dateTime={article.publishedAt}>
              {formatDate(article.publishedAt)}
            </time>
          </div>

          <h3 className="mt-2 font-semibold text-zinc-900 group-hover:text-indigo-600 dark:text-zinc-100 dark:group-hover:text-indigo-400">
            {article.title}
          </h3>

          <p className="mt-2 line-clamp-2 text-sm text-zinc-600 dark:text-zinc-400">
            {article.excerpt}
          </p>
        </div>
      </Card>
    </Link>
  );
}

interface NewsGridProps {
  articles: NewsArticle[];
  className?: string;
}

export function NewsGrid({ articles, className }: NewsGridProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3",
        className
      )}
    >
      {articles.map((article) => (
        <NewsCard key={article.slug} article={article} />
      ))}
    </div>
  );
}

