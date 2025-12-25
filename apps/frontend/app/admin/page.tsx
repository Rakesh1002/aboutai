"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Draft {
  id: string;
  title: string;
  type: "tool" | "news";
  status: "pending" | "approved" | "rejected";
  created_at: string;
  url?: string;
  trust_score?: number;
}

interface PipelineTask {
  id: string;
  name: string;
  status: "running" | "completed" | "failed" | "scheduled";
  last_run?: string;
  next_run?: string;
}

interface Stats {
  tools_indexed: number;
  news_articles: number;
  pending_drafts: number;
  newsletter_subscribers: number;
  sources_monitored: number;
}

export default function AdminDashboard() {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [tasks, setTasks] = useState<PipelineTask[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [activeTab, setActiveTab] = useState<"drafts" | "pipeline" | "stats">("drafts");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    const loadData = async () => {
      setLoading(true);
      
      // In production, fetch from API
      // const response = await fetch('/api/v1/admin/drafts');
      
      // Mock data for demo
      setDrafts([
        {
          id: "1",
          title: "Claude 3.5 Sonnet - Anthropic's Latest Model",
          type: "tool",
          status: "pending",
          created_at: new Date().toISOString(),
          url: "https://anthropic.com/claude",
          trust_score: 85,
        },
        {
          id: "2",
          title: "OpenAI Releases GPT-4 Turbo with Vision",
          type: "news",
          status: "pending",
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
        {
          id: "3",
          title: "Cursor AI - The AI-First Code Editor",
          type: "tool",
          status: "pending",
          created_at: new Date(Date.now() - 7200000).toISOString(),
          url: "https://cursor.so",
          trust_score: 78,
        },
      ]);

      setTasks([
        {
          id: "1",
          name: "Full Content Pipeline",
          status: "scheduled",
          last_run: new Date(Date.now() - 14400000).toISOString(),
          next_run: new Date(Date.now() + 3600000).toISOString(),
        },
        {
          id: "2",
          name: "Launch Sites Scraper",
          status: "completed",
          last_run: new Date(Date.now() - 7200000).toISOString(),
          next_run: new Date(Date.now() + 14400000).toISOString(),
        },
        {
          id: "3",
          name: "Podcast Directory Update",
          status: "completed",
          last_run: new Date(Date.now() - 86400000).toISOString(),
          next_run: new Date(Date.now() + 86400000).toISOString(),
        },
        {
          id: "4",
          name: "Weekly Newsletter",
          status: "scheduled",
          last_run: new Date(Date.now() - 604800000).toISOString(),
          next_run: new Date(Date.now() + 172800000).toISOString(),
        },
      ]);

      setStats({
        tools_indexed: 523,
        news_articles: 1247,
        pending_drafts: 12,
        newsletter_subscribers: 10432,
        sources_monitored: 25,
      });

      setLoading(false);
    };

    loadData();
  }, []);

  const handleAction = async (draftId: string, action: "approve" | "reject" | "regenerate") => {
    // In production, call API
    console.log(`${action} draft ${draftId}`);
    
    // Optimistic update
    setDrafts((prev) =>
      prev.map((d) =>
        d.id === draftId
          ? { ...d, status: action === "approve" ? "approved" : action === "reject" ? "rejected" : d.status }
          : d
      )
    );
  };

  const triggerPipeline = async (taskName: string) => {
    // In production, call API to trigger task
    console.log(`Triggering ${taskName}`);
    
    setTasks((prev) =>
      prev.map((t) =>
        t.name === taskName ? { ...t, status: "running" } : t
      )
    );
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      {/* Header */}
      <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
                Admin Dashboard
              </h1>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Content management and pipeline control
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                View Site
              </Button>
              <Button size="sm">Trigger Full Pipeline</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Stats Grid */}
        {stats && (
          <div className="grid gap-4 md:grid-cols-5 mb-8">
            <StatCard label="Tools Indexed" value={stats.tools_indexed} />
            <StatCard label="News Articles" value={stats.news_articles} />
            <StatCard label="Pending Drafts" value={stats.pending_drafts} highlight />
            <StatCard label="Newsletter Subs" value={stats.newsletter_subscribers.toLocaleString()} />
            <StatCard label="Sources" value={stats.sources_monitored} />
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1 mb-6 border-b border-zinc-200 dark:border-zinc-800">
          {(["drafts", "pipeline", "stats"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? "border-indigo-600 text-indigo-600"
                  : "border-transparent text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
            <p className="mt-4 text-zinc-600 dark:text-zinc-400">Loading...</p>
          </div>
        ) : (
          <>
            {/* Drafts Tab */}
            {activeTab === "drafts" && (
              <div className="space-y-4">
                {drafts.length === 0 ? (
                  <Card className="p-8 text-center">
                    <p className="text-zinc-600 dark:text-zinc-400">
                      No pending drafts to review
                    </p>
                  </Card>
                ) : (
                  drafts.map((draft) => (
                    <DraftCard
                      key={draft.id}
                      draft={draft}
                      onAction={handleAction}
                    />
                  ))
                )}
              </div>
            )}

            {/* Pipeline Tab */}
            {activeTab === "pipeline" && (
              <div className="space-y-4">
                {tasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onTrigger={() => triggerPipeline(task.name)}
                  />
                ))}
              </div>
            )}

            {/* Stats Tab */}
            {activeTab === "stats" && (
              <div className="grid gap-6 md:grid-cols-2">
                <Card className="p-6">
                  <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
                    Content Breakdown
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-zinc-600 dark:text-zinc-400">Tools</span>
                      <span className="font-medium">{stats?.tools_indexed}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-600 dark:text-zinc-400">News</span>
                      <span className="font-medium">{stats?.news_articles}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-600 dark:text-zinc-400">Podcasts</span>
                      <span className="font-medium">15</span>
                    </div>
                  </div>
                </Card>
                <Card className="p-6">
                  <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
                    Scraper Sources
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-zinc-600 dark:text-zinc-400">Product Hunt</span>
                      <span className="text-emerald-600">Active</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-600 dark:text-zinc-400">BetaList</span>
                      <span className="text-emerald-600">Active</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-600 dark:text-zinc-400">Indie Hackers</span>
                      <span className="text-emerald-600">Active</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-600 dark:text-zinc-400">RSS Feeds</span>
                      <span className="text-emerald-600">12 active</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-600 dark:text-zinc-400">HackerNews</span>
                      <span className="text-emerald-600">Active</span>
                    </div>
                  </div>
                </Card>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: number | string;
  highlight?: boolean;
}) {
  return (
    <Card className={`p-4 ${highlight ? "border-amber-500/50" : ""}`}>
      <p className="text-sm text-zinc-600 dark:text-zinc-400">{label}</p>
      <p
        className={`text-2xl font-bold ${
          highlight ? "text-amber-600" : "text-zinc-900 dark:text-zinc-100"
        }`}
      >
        {value}
      </p>
    </Card>
  );
}

function DraftCard({
  draft,
  onAction,
}: {
  draft: Draft;
  onAction: (id: string, action: "approve" | "reject" | "regenerate") => void;
}) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span
              className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                draft.type === "tool"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400"
              }`}
            >
              {draft.type}
            </span>
            {draft.trust_score && (
              <span className="text-xs text-zinc-500">
                Trust: {draft.trust_score}%
              </span>
            )}
          </div>
          <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
            {draft.title}
          </h3>
          {draft.url && (
            <a
              href={draft.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              {draft.url}
            </a>
          )}
          <p className="text-xs text-zinc-500 mt-1">
            Created {new Date(draft.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => onAction(draft.id, "reject")}
          >
            Reject
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onAction(draft.id, "regenerate")}
          >
            Regenerate
          </Button>
          <Button size="sm" onClick={() => onAction(draft.id, "approve")}>
            Approve
          </Button>
        </div>
      </div>
    </Card>
  );
}

function TaskCard({
  task,
  onTrigger,
}: {
  task: PipelineTask;
  onTrigger: () => void;
}) {
  const statusColors = {
    running: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    completed: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    failed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    scheduled: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-400",
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
              {task.name}
            </h3>
            <span
              className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[task.status]}`}
            >
              {task.status}
            </span>
          </div>
          <div className="text-sm text-zinc-600 dark:text-zinc-400">
            {task.last_run && (
              <span>Last: {new Date(task.last_run).toLocaleString()}</span>
            )}
            {task.next_run && (
              <span className="ml-4">
                Next: {new Date(task.next_run).toLocaleString()}
              </span>
            )}
          </div>
        </div>
        <Button
          size="sm"
          variant="outline"
          onClick={onTrigger}
          disabled={task.status === "running"}
        >
          {task.status === "running" ? "Running..." : "Run Now"}
        </Button>
      </div>
    </Card>
  );
}

