declare module "*.mdx" {
  import type { MDXComponents } from "mdx/types";

  export const frontmatter: {
    [key: string]: unknown;
  };

  export default function MDXContent(props: {
    components?: MDXComponents;
  }): JSX.Element;
}

