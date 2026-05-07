import type { MDXComponents } from "mdx/types";
import Image, { ImageProps } from "next/image";
import Link from "next/link";

function Callout({
  children,
  type = "info",
}: {
  children: React.ReactNode;
  type?: "info" | "warning" | "success" | "error";
}) {
  const styles = {
    info: "bg-blue-50 border-blue-500 text-blue-900 dark:bg-blue-950 dark:text-blue-100",
    warning:
      "bg-amber-50 border-amber-500 text-amber-900 dark:bg-amber-950 dark:text-amber-100",
    success:
      "bg-emerald-50 border-emerald-500 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100",
    error:
      "bg-red-50 border-red-500 text-red-900 dark:bg-red-950 dark:text-red-100",
  };
  return (
    <div className={`my-6 rounded-lg border-l-4 p-4 ${styles[type]}`}>
      {children}
    </div>
  );
}

function Verdict({
  state,
  children,
}: {
  state: "ship-it" | "trial-only" | "avoid";
  children: React.ReactNode;
}) {
  const styles = {
    "ship-it": {
      label: "Ship it",
      cls: "bg-emerald-50 border-emerald-500 dark:bg-emerald-950/40",
      pillCls:
        "bg-emerald-600 text-white dark:bg-emerald-500 dark:text-emerald-950",
    },
    "trial-only": {
      label: "Trial only",
      cls: "bg-amber-50 border-amber-500 dark:bg-amber-950/40",
      pillCls: "bg-amber-600 text-white dark:bg-amber-500 dark:text-amber-950",
    },
    avoid: {
      label: "Avoid",
      cls: "bg-red-50 border-red-500 dark:bg-red-950/40",
      pillCls: "bg-red-600 text-white dark:bg-red-500 dark:text-red-950",
    },
  } as const;
  const s = styles[state];
  return (
    <div className={`my-8 rounded-lg border-l-4 p-5 ${s.cls}`}>
      <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold">
        <span className={`rounded-full px-2 py-0.5 text-xs ${s.pillCls}`}>
          Verdict
        </span>
        <span className="text-zinc-900 dark:text-zinc-100">{s.label}</span>
      </div>
      <div className="text-zinc-800 dark:text-zinc-200">{children}</div>
    </div>
  );
}

function Receipt({
  label,
  children,
}: {
  label?: string;
  children: React.ReactNode;
}) {
  return (
    <figure className="my-6 rounded-lg border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-900">
      {label && (
        <figcaption className="mb-2 font-mono text-xs uppercase tracking-wider text-zinc-500">
          {label}
        </figcaption>
      )}
      <div className="font-mono text-xs leading-relaxed text-zinc-800 dark:text-zinc-200">
        {children}
      </div>
    </figure>
  );
}

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    h1: ({ children }) => (
      <h1 className="mb-6 text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="mb-4 mt-10 text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="mb-3 mt-8 text-xl font-semibold text-zinc-900 dark:text-zinc-100">
        {children}
      </h3>
    ),
    p: ({ children }) => (
      <p className="mb-4 leading-7 text-zinc-700 dark:text-zinc-300">
        {children}
      </p>
    ),
    a: ({ href, children }) => (
      <Link
        href={href || "#"}
        className="font-medium text-zinc-900 underline underline-offset-4 hover:text-zinc-700 dark:text-zinc-100 dark:hover:text-zinc-300"
      >
        {children}
      </Link>
    ),
    ul: ({ children }) => (
      <ul className="my-4 list-disc space-y-2 pl-6 text-zinc-700 dark:text-zinc-300">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="my-4 list-decimal space-y-2 pl-6 text-zinc-700 dark:text-zinc-300">
        {children}
      </ol>
    ),
    li: ({ children }) => <li className="leading-7">{children}</li>,
    blockquote: ({ children }) => (
      <blockquote className="my-6 border-l-4 border-zinc-300 pl-4 italic text-zinc-600 dark:border-zinc-700 dark:text-zinc-400">
        {children}
      </blockquote>
    ),
    code: ({ children }) => (
      <code className="rounded bg-zinc-100 px-1.5 py-0.5 font-mono text-sm text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100">
        {children}
      </code>
    ),
    pre: ({ children }) => (
      <pre className="my-6 overflow-x-auto rounded-lg bg-zinc-950 p-4 text-sm text-zinc-100">
        {children}
      </pre>
    ),
    img: (props) => (
      <Image
        sizes="100vw"
        style={{ width: "100%", height: "auto" }}
        className="my-6 rounded-lg"
        {...(props as ImageProps)}
        alt={props.alt || ""}
      />
    ),
    hr: () => <hr className="my-8 border-zinc-200 dark:border-zinc-800" />,
    table: ({ children }) => (
      <div className="my-6 overflow-x-auto">
        <table className="w-full text-left text-sm">{children}</table>
      </div>
    ),
    th: ({ children }) => (
      <th className="border-b border-zinc-200 bg-zinc-50 px-4 py-3 font-semibold text-zinc-900 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="border-b border-zinc-200 px-4 py-3 text-zinc-700 dark:border-zinc-800 dark:text-zinc-300">
        {children}
      </td>
    ),

    Callout,
    Verdict,
    Receipt,
    Image,
    Link,

    ...components,
  };
}
