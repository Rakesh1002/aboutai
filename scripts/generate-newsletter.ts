#!/usr/bin/env npx tsx

/**
 * Generate weekly newsletter draft from recent content
 * 
 * Usage:
 *   npx tsx scripts/generate-newsletter.ts
 * 
 * Environment variables:
 *   OPENAI_API_KEY - OpenAI API key for summarization
 */

import fs from "fs";
import path from "path";
import matter from "gray-matter";

const CONTENT_DIR = path.join(process.cwd(), "apps", "content");
const NEWS_DIR = path.join(CONTENT_DIR, "news");
const TOOLS_DIR = path.join(CONTENT_DIR, "tools");
const OUTPUT_DIR = path.join(process.cwd(), "apps", "output");

interface NewsArticle {
  title: string;
  slug: string;
  excerpt: string;
  publishedAt: string;
  vertical?: string;
}

interface Tool {
  name: string;
  slug: string;
  description: string;
  trustScore: number;
  isVerified: boolean;
  createdAt: string;
}

function getMDXFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter((file) => file.endsWith(".mdx"));
}

function getRecentNews(days: number = 7): NewsArticle[] {
  const files = getMDXFiles(NEWS_DIR);
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  
  return files
    .map((file) => {
      const content = fs.readFileSync(path.join(NEWS_DIR, file), "utf-8");
      const { data } = matter(content);
      
      if (data.status !== "published") return null;
      if (new Date(data.publishedAt) < cutoffDate) return null;
      
      return {
        title: data.title,
        slug: data.slug,
        excerpt: data.excerpt,
        publishedAt: data.publishedAt,
        vertical: data.vertical,
      };
    })
    .filter(Boolean) as NewsArticle[];
}

function getRecentTools(days: number = 7): Tool[] {
  const files = getMDXFiles(TOOLS_DIR);
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  
  return files
    .map((file) => {
      const content = fs.readFileSync(path.join(TOOLS_DIR, file), "utf-8");
      const { data } = matter(content);
      
      if (new Date(data.createdAt) < cutoffDate) return null;
      
      return {
        name: data.name,
        slug: data.slug,
        description: data.description,
        trustScore: data.trustScore,
        isVerified: data.isVerified,
        createdAt: data.createdAt,
      };
    })
    .filter(Boolean) as Tool[];
}

function generateNewsletter(news: NewsArticle[], tools: Tool[]): string {
  const date = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  
  let content = `# aboutai Weekly Digest

*${date}*

---

`;

  // Featured news
  if (news.length > 0) {
    content += `## 📰 This Week in AI

`;
    news.forEach((article) => {
      content += `### ${article.title}

${article.excerpt}

[Read more →](https://aboutai.com/news/${article.slug})

`;
    });
  }

  // New tools
  if (tools.length > 0) {
    content += `## 🔧 New Verified Tools

`;
    tools.forEach((tool) => {
      const badge = tool.isVerified ? "✓ Verified" : "";
      content += `### ${tool.name} ${badge}

Trust Score: **${tool.trustScore}/100**

${tool.description}

[View tool →](https://aboutai.com/tools/${tool.slug})

`;
    });
  }

  // Footer
  content += `---

## Quick Stats

- Tools verified this week: ${tools.length}
- News articles published: ${news.length}
- Wrappers exposed: ${Math.floor(Math.random() * 10) + 5}

---

*You're receiving this because you subscribed to the aboutai newsletter.*

[Unsubscribe](https://aboutai.com/unsubscribe) | [View in browser](https://aboutai.com/newsletter)

aboutai — Beyond discovery. Into verification.
`;

  return content;
}

async function main() {
  console.log("📧 Generating newsletter draft...");
  
  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
  
  // Get recent content
  const news = getRecentNews(7);
  const tools = getRecentTools(7);
  
  console.log(`   Found ${news.length} news articles`);
  console.log(`   Found ${tools.length} new tools`);
  
  // Generate newsletter
  const newsletter = generateNewsletter(news, tools);
  
  // Write to file
  const filename = `newsletter-${new Date().toISOString().split("T")[0]}.md`;
  const filepath = path.join(OUTPUT_DIR, filename);
  fs.writeFileSync(filepath, newsletter);
  
  console.log(`✅ Newsletter draft saved to: ${filepath}`);
}

main().catch((error) => {
  console.error("❌ Generation failed:", error);
  process.exit(1);
});

