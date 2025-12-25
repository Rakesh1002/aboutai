import Link from "next/link";
import { Card } from "@/components/ui/card";

// Curated list of AI podcasts (matches backend)
const AI_PODCASTS = [
  {
    id: "practical-ai",
    title: "Practical AI",
    description:
      "Making AI practical and productive for everyone. Daniel and Chris discuss ML and AI technologies, applications, and practices.",
    feed: "https://changelog.com/practicalai/feed",
    website: "https://changelog.com/practicalai",
    artwork: "https://cdn.changelog.com/uploads/covers/practicalai-original.png",
    categories: ["AI", "ML", "Production"],
  },
  {
    id: "twiml-ai",
    title: "TWIML AI Podcast",
    description:
      "Exploring interesting and important topics at the intersection of machine learning, AI, and data with thought leaders and practitioners.",
    feed: "https://feeds.megaphone.fm/MLN2155636147",
    website: "https://twimlai.com",
    artwork: "https://twimlai.com/wp-content/uploads/2018/05/twiml-new-cover.jpg",
    categories: ["AI", "ML", "Research"],
  },
  {
    id: "lex-fridman",
    title: "Lex Fridman Podcast",
    description:
      "Conversations about AI, science, technology, history, philosophy and the nature of intelligence, consciousness, and meaning.",
    feed: "https://lexfridman.com/feed/podcast/",
    website: "https://lexfridman.com/podcast/",
    artwork: "https://lexfridman.com/wordpress/wp-content/uploads/2021/05/lex-fridman-podcast-main.png",
    categories: ["AI", "Tech", "Philosophy"],
  },
  {
    id: "ml-street-talk",
    title: "Machine Learning Street Talk",
    description:
      "Technical discussions about machine learning with world-renowned researchers and practitioners.",
    feed: "https://anchor.fm/s/1e4a0eac/podcast/rss",
    website: "https://www.youtube.com/c/MachineLearningStreetTalk",
    artwork: "https://d3t3ozftmdmh3i.cloudfront.net/production/podcast_uploaded_nologo400/7636309/7636309-1616439760571-f04c0ce9e0c29.jpg",
    categories: ["ML", "Research", "Technical"],
  },
  {
    id: "gradient-dissent",
    title: "Gradient Dissent",
    description:
      "A show about ML in the real world. Interviews with ML practitioners about real-world ML applications.",
    feed: "https://feeds.soundcloud.com/users/soundcloud:users:774544815/sounds.rss",
    website: "https://wandb.ai/gradient-dissent",
    artwork: "https://wandb.ai/gradient-dissent/gradient-dissent-logo.png",
    categories: ["ML", "Industry", "Interviews"],
  },
  {
    id: "no-priors",
    title: "No Priors",
    description:
      "A show about AI with partners from A16Z. Deep conversations with the people building and shaping the future of AI.",
    feed: "https://feeds.megaphone.fm/nopriors",
    website: "https://www.nopriors.com/",
    artwork: "https://nopriors.com/no-priors-cover.jpg",
    categories: ["AI", "Startups", "VC"],
  },
  {
    id: "cognitive-revolution",
    title: "The Cognitive Revolution",
    description:
      "Exploring AI's transformative potential across industries. In-depth interviews with AI builders and thinkers.",
    feed: "https://feeds.transistor.fm/the-cognitive-revolution",
    website: "https://www.cognitiverevolution.ai/",
    artwork: "https://www.cognitiverevolution.ai/content/images/2023/06/TheCognitiveRevolution_Final_V3.jpg",
    categories: ["AI", "Industry", "Interviews"],
  },
  {
    id: "last-week-in-ai",
    title: "Last Week in AI",
    description:
      "Weekly news roundup covering the latest developments in artificial intelligence.",
    feed: "https://feeds.buzzsprout.com/2025445.rss",
    website: "https://lastweekin.ai/",
    artwork: "https://lastweekin.ai/last-week-in-ai-logo.png",
    categories: ["AI News", "Weekly"],
  },
  {
    id: "latent-space",
    title: "Latent Space",
    description:
      "The AI Engineering podcast. Technical deep dives into AI infrastructure, LLMs, and building AI products.",
    feed: "https://feeds.transistor.fm/latent-space",
    website: "https://www.latent.space/",
    artwork: "https://www.latent.space/latent-space-logo.png",
    categories: ["AI Engineering", "LLM", "Technical"],
  },
  {
    id: "eye-on-ai",
    title: "Eye on AI",
    description:
      "Hosted by longtime New York Times journalist Craig Smith, featuring discussions with AI leaders and experts.",
    feed: "https://feeds.megaphone.fm/eye-on-ai",
    website: "https://www.eye-on.ai/",
    artwork: "https://eye-on.ai/eye-on-ai-logo.jpg",
    categories: ["AI News", "Industry"],
  },
  {
    id: "nvidia-ai-podcast",
    title: "The AI Podcast (NVIDIA)",
    description:
      "NVIDIA's podcast exploring how AI is transforming industries and changing the world.",
    feed: "https://feeds.soundcloud.com/users/soundcloud:users:264034133/sounds.rss",
    website: "https://blogs.nvidia.com/ai-podcast/",
    artwork: "https://blogs.nvidia.com/wp-content/uploads/2020/04/AI-podcast.jpg",
    categories: ["AI", "Industry", "NVIDIA"],
  },
  {
    id: "data-skeptic",
    title: "Data Skeptic",
    description:
      "Features interviews and discussion of topics related to data science, statistics, ML, and AI from the perspective of applying skeptical methodology.",
    feed: "https://dataskeptic.libsyn.com/rss",
    website: "https://dataskeptic.com/",
    artwork: "https://dataskeptic.com/static/DataSkeptic-logo.png",
    categories: ["Data Science", "ML", "Education"],
  },
];

export default function PodcastsPage() {
  return (
    <div className="flex flex-col">
      {/* Header */}
      <section className="relative overflow-hidden border-b border-zinc-200 bg-gradient-to-b from-pink-50 to-white dark:border-zinc-800 dark:from-pink-950/20 dark:to-zinc-950">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)] bg-[size:14px_24px]" />
        <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white/80 px-4 py-1.5 text-sm backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/80">
              <span className="text-xl">🎙️</span>
              <span className="text-zinc-600 dark:text-zinc-400">
                {AI_PODCASTS.length} AI Podcasts
              </span>
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-5xl">
              AI Podcast Directory
            </h1>
            <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">
              Stay informed with the best podcasts about artificial intelligence,
              machine learning, and the future of tech.
            </p>
          </div>
        </div>
      </section>

      {/* Podcast Grid */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {AI_PODCASTS.map((podcast) => (
              <PodcastCard key={podcast.id} podcast={podcast} />
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t border-zinc-200 dark:border-zinc-800 py-16 bg-zinc-50 dark:bg-zinc-900">
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">
            Know a great AI podcast?
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400 mb-6">
            Help us grow this directory. Suggest a podcast and we&apos;ll review it
            for inclusion.
          </p>
          <Link
            href="mailto:podcasts@aboutai.com?subject=Podcast%20Suggestion"
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors"
          >
            Suggest a Podcast
          </Link>
        </div>
      </section>
    </div>
  );
}

function PodcastCard({
  podcast,
}: {
  podcast: (typeof AI_PODCASTS)[number];
}) {
  return (
    <Card className="group overflow-hidden transition-all hover:shadow-lg">
      <div className="p-6">
        <div className="flex gap-4">
          {/* Artwork placeholder */}
          <div className="flex-shrink-0 w-20 h-20 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-3xl text-white">
            🎙️
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
              {podcast.title}
            </h3>
            <div className="mt-1 flex flex-wrap gap-1.5">
              {podcast.categories.slice(0, 3).map((cat) => (
                <span
                  key={cat}
                  className="inline-flex rounded-full bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 text-[10px] font-medium text-zinc-600 dark:text-zinc-400"
                >
                  {cat}
                </span>
              ))}
            </div>
          </div>
        </div>
        <p className="mt-4 text-sm text-zinc-600 dark:text-zinc-400 line-clamp-3">
          {podcast.description}
        </p>
        <div className="mt-4 flex gap-3">
          <a
            href={podcast.website}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 text-center rounded-lg border border-zinc-200 dark:border-zinc-700 px-4 py-2 text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
          >
            Website
          </a>
          <a
            href={podcast.feed}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 text-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 transition-colors"
          >
            Subscribe
          </a>
        </div>
      </div>
    </Card>
  );
}

