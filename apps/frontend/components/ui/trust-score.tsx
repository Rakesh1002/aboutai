"use client";

import { cn, getTrustScoreBg, getTrustScoreLabel } from "@/lib/utils";

interface TrustScoreProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

export function TrustScore({
  score,
  size = "md",
  showLabel = false,
  className,
}: TrustScoreProps) {
  const sizeClasses = {
    sm: "h-8 w-8 text-xs",
    md: "h-12 w-12 text-sm",
    lg: "h-16 w-16 text-lg",
  };

  const ringSize = {
    sm: 28,
    md: 44,
    lg: 60,
  };

  const strokeWidth = {
    sm: 3,
    md: 4,
    lg: 5,
  };

  const radius = (ringSize[size] - strokeWidth[size]) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className={cn("relative", sizeClasses[size])}>
        {/* Background circle */}
        <svg
          className="absolute inset-0 -rotate-90"
          width={ringSize[size]}
          height={ringSize[size]}
        >
          <circle
            cx={ringSize[size] / 2}
            cy={ringSize[size] / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth[size]}
            className="text-zinc-200 dark:text-zinc-800"
          />
          <circle
            cx={ringSize[size] / 2}
            cy={ringSize[size] / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth[size]}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className={cn(
              "transition-all duration-500",
              getTrustScoreBg(score).replace("bg-", "text-")
            )}
          />
        </svg>
        {/* Score number */}
        <div className="absolute inset-0 flex items-center justify-center font-bold text-zinc-900 dark:text-zinc-100">
          {score}
        </div>
      </div>
      {showLabel && (
        <div className="flex flex-col">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
            Trust Score
          </span>
          <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
            {getTrustScoreLabel(score)}
          </span>
        </div>
      )}
    </div>
  );
}

interface TrustScoreBadgeProps {
  score: number;
  className?: string;
}

export function TrustScoreBadge({ score, className }: TrustScoreBadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-sm font-medium",
        "bg-zinc-900 text-white dark:bg-white dark:text-zinc-900",
        className
      )}
    >
      <span className={cn("h-2 w-2 rounded-full", getTrustScoreBg(score))} />
      <span>{score}</span>
    </div>
  );
}

