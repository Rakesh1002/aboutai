import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { NewsletterSignup } from "@/components/newsletter-signup";

// Course data
const COURSES = [
  {
    id: "ai-fundamentals",
    title: "AI Fundamentals for Developers",
    description:
      "Master the core concepts of AI and ML. From neural networks to transformers, understand how modern AI works under the hood.",
    duration: "6 weeks",
    level: "Beginner",
    modules: 12,
    price: "$299",
    status: "coming-soon" as const,
    topics: ["Neural Networks", "Transformers", "Embeddings", "Fine-tuning"],
    instructor: "Dr. Sarah Chen",
  },
  {
    id: "llm-engineering",
    title: "LLM Engineering Masterclass",
    description:
      "Production-grade LLM applications. Learn RAG, prompt engineering, evaluation frameworks, and deployment best practices.",
    duration: "8 weeks",
    level: "Intermediate",
    modules: 16,
    price: "$499",
    status: "coming-soon" as const,
    topics: ["RAG Systems", "Prompt Engineering", "Evaluation", "Deployment"],
    instructor: "Alex Rivera",
  },
  {
    id: "ai-product-management",
    title: "AI Product Management",
    description:
      "Ship AI products that users love. Understand capabilities, limitations, and how to scope AI features realistically.",
    duration: "4 weeks",
    level: "All Levels",
    modules: 8,
    price: "$199",
    status: "coming-soon" as const,
    topics: ["AI Capabilities", "Scoping", "Ethics", "Go-to-Market"],
    instructor: "Maya Patel",
  },
  {
    id: "ai-security",
    title: "AI Security & Red Teaming",
    description:
      "Secure your AI systems. Learn about prompt injection, jailbreaks, model theft, and how to defend against them.",
    duration: "4 weeks",
    level: "Advanced",
    modules: 8,
    price: "$349",
    status: "coming-soon" as const,
    topics: ["Prompt Injection", "Jailbreaks", "Data Poisoning", "Defenses"],
    instructor: "James Wu",
  },
];

const RESOURCES = [
  {
    title: "AI Tool Evaluation Guide",
    description: "How to evaluate AI tools like a pro. Our comprehensive framework for assessing reliability and value.",
    type: "Guide",
    icon: "📖",
  },
  {
    title: "Wrapper Detection Checklist",
    description: "20-point checklist to identify thin wrappers vs. genuine AI innovation.",
    type: "Checklist",
    icon: "✅",
  },
  {
    title: "AI Architecture Patterns",
    description: "Common architectural patterns for production AI systems. RAG, agents, fine-tuning, and more.",
    type: "Reference",
    icon: "🏗️",
  },
  {
    title: "Prompt Engineering Templates",
    description: "Battle-tested prompt templates for various use cases. Copy, adapt, and improve.",
    type: "Templates",
    icon: "📝",
  },
];

export default function LearnPage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-zinc-200 bg-gradient-to-b from-emerald-50 to-white dark:border-zinc-800 dark:from-emerald-950/20 dark:to-zinc-950">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)] bg-[size:14px_24px]" />
        <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white/80 px-4 py-1.5 text-sm backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/80">
              <span className="text-xl">🎓</span>
              <span className="text-zinc-600 dark:text-zinc-400">
                Launching Q1 2025
              </span>
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100 sm:text-5xl">
              Learn AI the Right Way
            </h1>
            <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">
              Cohort-based courses taught by practitioners, not academics.
              Architectural patterns, not prompting tricks. Get certified.
            </p>
            <div className="mt-8 flex justify-center gap-4">
              <Button size="lg" disabled>
                Join Waitlist
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="#resources">Free Resources</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Courses Grid */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
              Upcoming Courses
            </h2>
            <p className="mt-2 text-zinc-600 dark:text-zinc-400">
              Expert-led, cohort-based learning with real projects
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2">
            {COURSES.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        </div>
      </section>

      {/* Why Learn With Us */}
      <section className="border-t border-zinc-200 dark:border-zinc-800 py-16 bg-zinc-50 dark:bg-zinc-900/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-12">
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
              Why Learn With aboutai?
            </h2>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            <div className="text-center">
              <div className="mx-auto w-14 h-14 rounded-2xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center text-2xl mb-4">
                👨‍💻
              </div>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                Practitioner-Led
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Learn from engineers building production AI systems, not
                researchers or influencers.
              </p>
            </div>
            <div className="text-center">
              <div className="mx-auto w-14 h-14 rounded-2xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-2xl mb-4">
                🏗️
              </div>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                Architecture Focus
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                We teach patterns that last, not tricks that break with the next
                model release.
              </p>
            </div>
            <div className="text-center">
              <div className="mx-auto w-14 h-14 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-2xl mb-4">
                🤝
              </div>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
                Cohort Community
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Learn alongside peers, get feedback on your projects, and build
                your network.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Free Resources */}
      <section id="resources" className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
              Free Resources
            </h2>
            <p className="mt-2 text-zinc-600 dark:text-zinc-400">
              Start learning now with our free guides and templates
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {RESOURCES.map((resource) => (
              <Card
                key={resource.title}
                className="p-6 group cursor-pointer hover:shadow-lg transition-all"
              >
                <div className="w-12 h-12 rounded-xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-2xl mb-4">
                  {resource.icon}
                </div>
                <span className="text-xs font-medium text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
                  {resource.type}
                </span>
                <h3 className="mt-2 font-semibold text-zinc-900 dark:text-zinc-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  {resource.title}
                </h3>
                <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400 line-clamp-2">
                  {resource.description}
                </p>
                <div className="mt-4 text-sm font-medium text-indigo-600 dark:text-indigo-400">
                  Coming Soon →
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter CTA */}
      <section className="border-t border-zinc-200 dark:border-zinc-800 py-16 bg-zinc-50 dark:bg-zinc-900">
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">
            Get Early Access
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400 mb-8">
            Be the first to know when courses launch. Plus, get exclusive
            discounts and free resources.
          </p>
          <NewsletterSignup />
        </div>
      </section>
    </div>
  );
}

function CourseCard({ course }: { course: (typeof COURSES)[number] }) {
  const levelColors = {
    Beginner: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    Intermediate: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    Advanced: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    "All Levels": "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400",
  };

  return (
    <Card className="overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex gap-2">
            <span
              className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${levelColors[course.level as keyof typeof levelColors]}`}
            >
              {course.level}
            </span>
            <span className="inline-flex rounded-full bg-zinc-100 dark:bg-zinc-800 px-2.5 py-0.5 text-xs font-medium text-zinc-600 dark:text-zinc-400">
              {course.duration}
            </span>
          </div>
          <span className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
            {course.price}
          </span>
        </div>

        <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
          {course.title}
        </h3>
        <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
          {course.description}
        </p>

        <div className="flex flex-wrap gap-2 mb-6">
          {course.topics.map((topic) => (
            <span
              key={topic}
              className="inline-flex rounded-lg bg-zinc-100 dark:bg-zinc-800 px-2 py-1 text-xs text-zinc-600 dark:text-zinc-400"
            >
              {topic}
            </span>
          ))}
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-zinc-200 dark:border-zinc-800">
          <div className="text-sm text-zinc-600 dark:text-zinc-400">
            <span className="font-medium text-zinc-900 dark:text-zinc-100">
              {course.instructor}
            </span>
            <span className="mx-2">•</span>
            <span>{course.modules} modules</span>
          </div>
          <Button variant="outline" size="sm" disabled>
            Notify Me
          </Button>
        </div>
      </div>
    </Card>
  );
}

