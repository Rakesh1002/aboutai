import { Metadata } from "next";
import { getAllToolsAsync, getAllCategories, getAllVerticals } from "@/lib/content";
import { ToolGrid } from "@/components/tools/tool-card";
import { Button } from "@/components/ui/button";

export const metadata: Metadata = {
  title: "AI Tools Directory",
  description:
    "Discover verified AI tools with Trust Scores. Filter by category, vertical, and wrapper status. Find native AI, not wrappers.",
};

// Revalidate every 60 seconds for fresh content
export const revalidate = 60;

export default async function ToolsPage() {
  const tools = await getAllToolsAsync();
  const categories = getAllCategories();
  const verticals = getAllVerticals();

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
          AI Tools Directory
        </h1>
        <p className="mt-2 text-lg text-zinc-600 dark:text-zinc-400">
          Verified tools with Trust Scores. No wrappers hiding as innovation.
        </p>
      </div>

      {/* Filters */}
      <div className="mb-8 flex flex-wrap gap-4 border-b border-zinc-200 pb-6 dark:border-zinc-800">
        <div>
          <label className="mb-2 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Vertical
          </label>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" size="sm">
              All
            </Button>
            {verticals.map((vertical) => (
              <Button key={vertical} variant="outline" size="sm">
                {vertical.charAt(0).toUpperCase() + vertical.slice(1)}
              </Button>
            ))}
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Category
          </label>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" size="sm">
              All
            </Button>
            {categories.slice(0, 5).map((category) => (
              <Button key={category} variant="outline" size="sm">
                {category}
              </Button>
            ))}
            {categories.length > 5 && (
              <Button variant="ghost" size="sm">
                +{categories.length - 5} more
              </Button>
            )}
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Type
          </label>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" size="sm">
              All
            </Button>
            <Button variant="outline" size="sm">
              ⚡ Native
            </Button>
            <Button variant="outline" size="sm">
              🎯 Fine-Tuned
            </Button>
            <Button variant="outline" size="sm">
              📚 RAG
            </Button>
            <Button variant="outline" size="sm">
              📦 Wrappers
            </Button>
          </div>
        </div>
      </div>

      {/* Results count */}
      <div className="mb-6 flex items-center justify-between">
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Showing <span className="font-medium">{tools.length}</span> tools
        </p>
        <select className="rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-sm dark:border-zinc-800 dark:bg-zinc-950">
          <option>Sort by Trust Score</option>
          <option>Sort by Name</option>
          <option>Sort by Recently Added</option>
          <option>Sort by Recently Audited</option>
        </select>
      </div>

      {/* Tools Grid */}
      {tools.length > 0 ? (
        <ToolGrid tools={tools} />
      ) : (
        <div className="py-12 text-center">
          <p className="text-lg text-zinc-600 dark:text-zinc-400">
            No tools found. Check back soon!
          </p>
          <p className="mt-2 text-sm text-zinc-500">
            We&apos;re continuously adding and verifying new AI tools.
          </p>
        </div>
      )}

      {/* Pagination placeholder */}
      {tools.length > 12 && (
        <div className="mt-12 flex justify-center gap-2">
          <Button variant="outline" size="sm" disabled>
            Previous
          </Button>
          <Button variant="secondary" size="sm">
            1
          </Button>
          <Button variant="outline" size="sm">
            2
          </Button>
          <Button variant="outline" size="sm">
            3
          </Button>
          <Button variant="outline" size="sm">
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

