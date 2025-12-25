import { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { getToolBySlug, getAllTools } from "@/lib/content";
import { TrustScoreBadge } from "@/components/ui/trust-score";
import { WrapperIndicator } from "@/components/ui/wrapper-status";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface ToolPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const tools = getAllTools();
  return tools.map((tool) => ({
    slug: tool.slug,
  }));
}

export async function generateMetadata({
  params,
}: ToolPageProps): Promise<Metadata> {
  const { slug } = await params;
  const tool = getToolBySlug(slug);

  if (!tool) {
    return {
      title: "Tool Not Found",
    };
  }

  return {
    title: `${tool.name} - AI Tool Review & Trust Score`,
    description: tool.description,
  };
}

export default async function ToolPage({ params }: ToolPageProps) {
  const { slug } = await params;
  const tool = getToolBySlug(slug);

  if (!tool) {
    notFound();
  }

  // Determine wrapper description
  const wrapperDescriptions: Record<string, string> = {
    native: "Native AI application with proprietary technology",
    fine_tuned: "Uses fine-tuned models for domain expertise",
    rag: "RAG-enhanced with proprietary knowledge base",
    wrapper: "UI layer over foundation model APIs",
    unknown: "Technology stack not yet verified",
  };

  const wrapperDesc =
    wrapperDescriptions[tool.wrapperStatus] || "Unknown technology stack";

  // Get trust level color
  const getTrustColor = (score: number) => {
    if (score >= 70) return "text-emerald-600 dark:text-emerald-400";
    if (score >= 40) return "text-amber-600 dark:text-amber-400";
    return "text-red-600 dark:text-red-400";
  };

  // First letter for logo fallback
  const logoColor = {
    c: "bg-amber-500",
    g: "bg-emerald-500",
  }[tool.name.charAt(0).toLowerCase()] || "bg-indigo-500";

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Breadcrumb */}
      <nav className="mb-8">
        <ol className="flex items-center gap-2 text-sm text-zinc-500">
          <li>
            <Link href="/" className="hover:text-zinc-700 dark:hover:text-zinc-300">
              Home
            </Link>
          </li>
          <li>/</li>
          <li>
            <Link href="/tools" className="hover:text-zinc-700 dark:hover:text-zinc-300">
              Tools
            </Link>
          </li>
          <li>/</li>
          <li className="text-zinc-900 dark:text-zinc-100">{tool.name}</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="mb-8 flex items-start gap-6">
        {/* Logo */}
        <div
          className={`flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl text-3xl font-bold text-white ${logoColor}`}
        >
          {tool.name.charAt(0).toUpperCase()}
        </div>

        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
                {tool.name}
              </h1>
              <p className="mt-2 text-lg text-zinc-600 dark:text-zinc-400">
                {tool.description}
              </p>
            </div>
            <TrustScoreBadge score={tool.trustScore} size="lg" />
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-3">
            <WrapperIndicator status={tool.wrapperStatus} />

            {tool.isVerified && (
              <span className="inline-flex items-center gap-1 rounded-md bg-indigo-50 px-2.5 py-1 text-sm font-medium text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
                ✓ Verified
              </span>
            )}

            <span className="rounded-md bg-zinc-100 px-2.5 py-1 text-sm text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {tool.vertical.charAt(0).toUpperCase() + tool.vertical.slice(1)}
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="mb-8 flex gap-3">
        <Button asChild>
          <a href={tool.url} target="_blank" rel="noopener noreferrer">
            Visit Website →
          </a>
        </Button>
        <Button variant="outline">Submit Update</Button>
      </div>

      {/* Trust Analysis Card */}
      <Card className="mb-8 p-6">
        <h2 className="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">
          Trust Analysis
        </h2>

        <div
          className={`mb-4 rounded-lg p-4 ${
            tool.trustScore >= 70
              ? "bg-emerald-50 dark:bg-emerald-950/50"
              : tool.trustScore >= 40
                ? "bg-amber-50 dark:bg-amber-950/50"
                : "bg-red-50 dark:bg-red-950/50"
          }`}
        >
          <p className={`font-medium ${getTrustColor(tool.trustScore)}`}>
            {tool.isVerified ? "Verified " : ""}
            {tool.wrapperStatus.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase())}
          </p>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            {wrapperDesc}
          </p>
        </div>

        <div className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
          <table className="w-full text-sm">
            <thead className="bg-zinc-50 dark:bg-zinc-900">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Factor
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Score
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Notes
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
              <tr>
                <td className="px-4 py-3 text-zinc-900 dark:text-zinc-100">
                  Overall Trust
                </td>
                <td className={`px-4 py-3 font-semibold ${getTrustColor(tool.trustScore)}`}>
                  {tool.trustScore}/100
                </td>
                <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                  Weighted average of all factors
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* Tags */}
      {tool.tags.length > 0 && (
        <Card className="mb-8 p-6">
          <h2 className="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">
            Technologies & Tags
          </h2>
          <div className="flex flex-wrap gap-2">
            {tool.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-zinc-100 px-3 py-1 text-sm text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
              >
                {tag}
              </span>
            ))}
          </div>
        </Card>
      )}

      {/* Pricing */}
      <Card className="mb-8 p-6">
        <h2 className="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">
          Pricing
        </h2>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            {tool.pricing.type === "free"
              ? "Free"
              : tool.pricing.startingPrice
                ? `$${tool.pricing.startingPrice}`
                : tool.pricing.type.charAt(0).toUpperCase() + tool.pricing.type.slice(1)}
          </span>
          {tool.pricing.startingPrice && tool.pricing.billingPeriod && (
            <span className="text-zinc-500">/{tool.pricing.billingPeriod}</span>
          )}
        </div>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          Pricing model: {tool.pricing.type}
        </p>
      </Card>

      {/* Categories */}
      <Card className="mb-8 p-6">
        <h2 className="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">
          Categories
        </h2>
        <div className="flex flex-wrap gap-2">
          {tool.categories.map((category) => (
            <Link
              key={category}
              href={`/tools?category=${encodeURIComponent(category)}`}
              className="rounded-lg bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-600 hover:bg-indigo-100 dark:bg-indigo-950 dark:text-indigo-400 dark:hover:bg-indigo-900"
            >
              {category}
            </Link>
          ))}
        </div>
      </Card>

      {/* Audit Info */}
      <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">
        Last audited:{" "}
        {tool.lastAuditedAt
          ? new Date(tool.lastAuditedAt).toLocaleDateString("en-US", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })
          : "Not yet audited"}
      </p>
    </div>
  );
}

