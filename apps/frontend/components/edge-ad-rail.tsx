import { adClickUrl, pickAd } from "@/lib/ads";

interface EdgeAdRailProps {
  side: "left" | "right";
}

export function EdgeAdRail({ side }: EdgeAdRailProps) {
  const seed = Math.floor(Math.random() * 1_000_000);
  const ad = pickAd(side, seed);
  if (!ad) return null;

  const isExternal = /^https?:\/\//.test(ad.url);
  const labelByClass = {
    sponsor: "Sponsor",
    exchange: "Partner",
    house: "From aboutai",
  } as const;

  // Sticky narrow vertical rail. Hidden < md. Doesn't push main content
  // because main is centered max-w-3xl and the rails sit in the gutter.
  const sideClass =
    side === "left"
      ? "left-4 xl:left-8"
      : "right-4 xl:right-8";

  return (
    <aside
      className={`pointer-events-none fixed top-24 ${sideClass} z-30 hidden w-44 md:block xl:w-52`}
      aria-label={`${side} sidebar advertisement`}
    >
      <a
        href={isExternal ? adClickUrl(ad.id) : ad.url}
        target={isExternal ? "_blank" : undefined}
        rel={isExternal ? "noopener sponsored" : undefined}
        className="pointer-events-auto group block rounded-lg border border-zinc-200 bg-white p-4 shadow-sm transition-colors hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-700"
      >
        <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
          {labelByClass[ad.klass]}
        </p>
        <p className="text-sm font-semibold leading-snug text-zinc-900 dark:text-zinc-100">
          {ad.headline}
        </p>
        {ad.subhead && (
          <p className="mt-2 text-xs leading-snug text-zinc-600 dark:text-zinc-400">
            {ad.subhead}
          </p>
        )}
        <p className="mt-3 text-xs font-medium text-zinc-900 group-hover:underline dark:text-zinc-100">
          {ad.cta} →
        </p>
      </a>
    </aside>
  );
}
