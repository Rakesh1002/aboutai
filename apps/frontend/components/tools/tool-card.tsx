"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Card } from "@/components/ui/card";
import { TrustScoreBadge } from "@/components/ui/trust-score";
import { WrapperIndicator } from "@/components/ui/wrapper-status";
import { cn } from "@/lib/utils";
import type { Tool } from "@/lib/content";

// Tool logo colors based on first letter
const logoColors: Record<string, string> = {
  a: "bg-rose-500",
  b: "bg-orange-500",
  c: "bg-amber-500",
  d: "bg-yellow-500",
  e: "bg-lime-500",
  f: "bg-green-500",
  g: "bg-emerald-500",
  h: "bg-teal-500",
  i: "bg-cyan-500",
  j: "bg-sky-500",
  k: "bg-blue-500",
  l: "bg-indigo-500",
  m: "bg-violet-500",
  n: "bg-purple-500",
  o: "bg-fuchsia-500",
  p: "bg-pink-500",
  q: "bg-rose-500",
  r: "bg-red-500",
  s: "bg-orange-500",
  t: "bg-amber-500",
  u: "bg-yellow-500",
  v: "bg-lime-500",
  w: "bg-green-500",
  x: "bg-emerald-500",
  y: "bg-teal-500",
  z: "bg-cyan-500",
};

function ToolLogo({ name, logoUrl }: { name: string; logoUrl?: string }) {
  const [imgError, setImgError] = useState(false);
  const firstChar = name.charAt(0).toLowerCase();
  const bgColor = logoColors[firstChar] || "bg-indigo-500";

  if (logoUrl && !imgError) {
    return (
      <Image
        src={logoUrl}
        alt={`${name} logo`}
        fill
        className="object-cover"
        onError={() => setImgError(true)}
        unoptimized
      />
    );
  }

  return (
    <div
      className={cn(
        "flex h-full w-full items-center justify-center text-lg font-bold text-white",
        bgColor
      )}
    >
      {name.charAt(0).toUpperCase()}
    </div>
  );
}

interface ToolCardProps {
  tool: Tool;
  className?: string;
}

export function ToolCard({ tool, className }: ToolCardProps) {
  return (
    <Link href={`/tools/${tool.slug}`}>
      <Card hover className={cn("group h-full p-5", className)}>
        <div className="flex items-start gap-4">
          {/* Logo */}
          <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-lg bg-zinc-100 dark:bg-zinc-800">
            <ToolLogo name={tool.name} logoUrl={tool.logoUrl} />
          </div>

          {/* Content */}
          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold text-zinc-900 group-hover:text-indigo-600 dark:text-zinc-100 dark:group-hover:text-indigo-400">
                {tool.name}
              </h3>
              <TrustScoreBadge score={tool.trustScore} />
            </div>

            <p className="mt-1.5 line-clamp-2 text-sm text-zinc-600 dark:text-zinc-400">
              {tool.description}
            </p>

            <div className="mt-3 flex flex-wrap items-center gap-2">
              <WrapperIndicator status={tool.wrapperStatus} showTooltip={false} />
              
              {tool.isVerified && (
                <span className="inline-flex items-center gap-1 rounded-md bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
                  ✓ Verified
                </span>
              )}

              {tool.pricing.type === "free" && (
                <span className="text-xs text-zinc-500 dark:text-zinc-400">
                  Free
                </span>
              )}
              {tool.pricing.type === "freemium" && tool.pricing.startingPrice && (
                <span className="text-xs text-zinc-500 dark:text-zinc-400">
                  From ${tool.pricing.startingPrice}/mo
                </span>
              )}
            </div>
          </div>
        </div>
      </Card>
    </Link>
  );
}

interface ToolGridProps {
  tools: Tool[];
  className?: string;
}

export function ToolGrid({ tools, className }: ToolGridProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3",
        className
      )}
    >
      {tools.map((tool) => (
        <ToolCard key={tool.slug} tool={tool} />
      ))}
    </div>
  );
}

