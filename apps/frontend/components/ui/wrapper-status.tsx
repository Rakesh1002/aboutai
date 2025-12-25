"use client";

import { cn, getWrapperStatusLabel, getWrapperStatusColor } from "@/lib/utils";

type WrapperStatus = "native" | "fine_tuned" | "rag" | "wrapper" | "unknown";

interface WrapperStatusBadgeProps {
  status: WrapperStatus;
  className?: string;
}

export function WrapperStatusBadge({
  status,
  className,
}: WrapperStatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium",
        getWrapperStatusColor(status),
        className
      )}
    >
      {getWrapperStatusLabel(status)}
    </span>
  );
}

interface WrapperIndicatorProps {
  status: WrapperStatus;
  showTooltip?: boolean;
  className?: string;
}

const statusIcons: Record<WrapperStatus, string> = {
  native: "⚡",
  fine_tuned: "🎯",
  rag: "📚",
  wrapper: "📦",
  unknown: "❓",
};

const statusDescriptions: Record<WrapperStatus, string> = {
  native: "Built on proprietary AI infrastructure",
  fine_tuned: "Uses custom fine-tuned models",
  rag: "Implements retrieval-augmented generation",
  wrapper: "UI layer over existing AI APIs",
  unknown: "Technical architecture not verified",
};

export function WrapperIndicator({
  status,
  showTooltip = true,
  className,
}: WrapperIndicatorProps) {
  return (
    <div className={cn("group relative inline-flex", className)}>
      <span
        className={cn(
          "inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium",
          getWrapperStatusColor(status)
        )}
      >
        <span>{statusIcons[status]}</span>
        <span>{getWrapperStatusLabel(status)}</span>
      </span>

      {showTooltip && (
        <div className="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 opacity-0 transition-opacity group-hover:opacity-100">
          <div className="whitespace-nowrap rounded-lg bg-zinc-900 px-3 py-2 text-xs text-white shadow-lg dark:bg-white dark:text-zinc-900">
            {statusDescriptions[status]}
          </div>
          <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-zinc-900 dark:border-t-white" />
        </div>
      )}
    </div>
  );
}
