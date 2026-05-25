-- Aggregator pipeline tables.
--
-- Three roles:
--   aggregator_sources : the curated RSS feed list (toggleable, weightable).
--   aggregator_seen    : dedupe ledger keyed by URL hash. Prevents re-pitching
--                        the same story across daily runs.
--   daily_drafts       : one JSON blob per date. The cron writes a "draft" row;
--                        a human edits content/daily/YYYY-MM-DD.ts and flips
--                        the row's status to "published" once the edit lands.
--                        Drafts are advisory — the build still imports the
--                        TS module from the repo. The DB row is the LLM's
--                        first pass + the audit trail.

CREATE TABLE IF NOT EXISTS aggregator_sources (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL CHECK (kind IN ('rss', 'atom')),
  region TEXT NOT NULL CHECK (region IN ('india', 'global')),
  weight REAL NOT NULL DEFAULT 1.0,
  enabled INTEGER NOT NULL DEFAULT 1,
  last_fetched_at INTEGER,
  last_status TEXT,
  last_error TEXT,
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sources_enabled ON aggregator_sources(enabled);

CREATE TABLE IF NOT EXISTS aggregator_seen (
  url_hash TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  source_id TEXT,
  first_seen_at INTEGER NOT NULL,
  used_in_date TEXT,
  FOREIGN KEY (source_id) REFERENCES aggregator_sources(id)
);

CREATE INDEX IF NOT EXISTS idx_seen_first_seen ON aggregator_seen(first_seen_at);
CREATE INDEX IF NOT EXISTS idx_seen_used_in ON aggregator_seen(used_in_date);

CREATE TABLE IF NOT EXISTS daily_drafts (
  date TEXT PRIMARY KEY,
  status TEXT NOT NULL CHECK (
    status IN ('draft', 'reviewed', 'published', 'discarded')
  ),
  payload TEXT NOT NULL,
  candidate_count INTEGER NOT NULL,
  shortlist_count INTEGER NOT NULL,
  generator TEXT NOT NULL,
  generator_model TEXT,
  generated_at INTEGER NOT NULL,
  reviewed_at INTEGER,
  notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_drafts_status ON daily_drafts(status);
CREATE INDEX IF NOT EXISTS idx_drafts_generated ON daily_drafts(generated_at);
