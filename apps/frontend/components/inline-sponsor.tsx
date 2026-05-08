import { getSponsorById, pickHouseSponsor, sponsorClickUrl } from "@/lib/sponsors";

interface InlineSponsorProps {
  sponsorId?: string;
}

export function InlineSponsor({ sponsorId }: InlineSponsorProps) {
  const sponsor =
    (sponsorId && getSponsorById(sponsorId)) ||
    pickHouseSponsor(Math.floor(Math.random() * 1_000_000));
  if (!sponsor) return null;

  const isExternal = /^https?:\/\//.test(sponsor.url);
  const labelByClass = {
    sponsor: "Today's sponsor",
    exchange: "Partner",
    house: "From aboutai",
  } as const;

  return (
    <aside
      className="my-8 rounded-xl border border-zinc-200 bg-zinc-50 p-5 dark:border-zinc-800 dark:bg-zinc-900"
      aria-label="sponsored content"
    >
      <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
        {labelByClass[sponsor.klass]}
      </p>
      <a
        href={isExternal ? sponsorClickUrl(sponsor.id) : sponsor.url}
        target={isExternal ? "_blank" : undefined}
        rel={isExternal ? "noopener sponsored" : undefined}
        className="group block"
      >
        <p className="text-base font-semibold leading-snug text-zinc-900 dark:text-zinc-100">
          {sponsor.headline}
        </p>
        <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
          {sponsor.body}
        </p>
        <p className="mt-3 text-sm font-medium text-zinc-900 group-hover:underline dark:text-zinc-100">
          {sponsor.cta} →
        </p>
      </a>
    </aside>
  );
}
