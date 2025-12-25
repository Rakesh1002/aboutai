-- ===========================================
-- aboutai Database Schema
-- Run this in Supabase SQL Editor
-- ===========================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- For semantic search

-- ===========================================
-- Tools Table
-- ===========================================
CREATE TABLE IF NOT EXISTS tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    
    -- Trust Engine scores
    trust_score INT CHECK (trust_score >= 0 AND trust_score <= 100),
    wrapper_status TEXT CHECK (wrapper_status IN ('native', 'fine_tuned', 'rag', 'wrapper', 'unknown')),
    wrapper_confidence FLOAT CHECK (wrapper_confidence >= 0 AND wrapper_confidence <= 1),
    
    -- Categorization
    category TEXT,
    vertical TEXT,
    pricing TEXT,
    tags TEXT[] DEFAULT '{}',
    
    -- Media
    logo_url TEXT,
    screenshot_url TEXT,
    
    -- Source tracking
    source TEXT, -- 'producthunt', 'betalist', 'submission', 'manual'
    source_id TEXT, -- ID from source platform
    
    -- Content
    content_mdx TEXT, -- Generated MDX content
    
    -- Status
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'rejected', 'archived')),
    
    -- Metadata (flexible JSON)
    metadata JSONB DEFAULT '{}',
    
    -- Vector embedding for semantic search (OpenAI ada-002 = 1536 dimensions)
    embedding VECTOR(1536),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

-- Indexes for tools
CREATE INDEX IF NOT EXISTS idx_tools_status ON tools(status);
CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category);
CREATE INDEX IF NOT EXISTS idx_tools_vertical ON tools(vertical);
CREATE INDEX IF NOT EXISTS idx_tools_source ON tools(source);
CREATE INDEX IF NOT EXISTS idx_tools_slug ON tools(slug);
CREATE INDEX IF NOT EXISTS idx_tools_url ON tools(url);
CREATE INDEX IF NOT EXISTS idx_tools_created_at ON tools(created_at DESC);

-- Full-text search index for tools
CREATE INDEX IF NOT EXISTS idx_tools_fts ON tools 
    USING GIN (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')));

-- ===========================================
-- News Table
-- ===========================================
CREATE TABLE IF NOT EXISTS news (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source_url TEXT,
    source_name TEXT, -- 'TechCrunch', 'MIT News', etc.
    
    -- Content
    summary TEXT,
    content TEXT,
    content_mdx TEXT,
    
    -- Analysis
    hype_score INT CHECK (hype_score >= 0 AND hype_score <= 100),
    hype_indicators TEXT[] DEFAULT '{}',
    
    -- Categorization
    vertical TEXT,
    tags TEXT[] DEFAULT '{}',
    
    -- Media
    image_url TEXT,
    
    -- Metadata
    author TEXT,
    metadata JSONB DEFAULT '{}',
    
    -- Vector embedding
    embedding VECTOR(1536),
    
    -- Timestamps
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for news
CREATE INDEX IF NOT EXISTS idx_news_slug ON news(slug);
CREATE INDEX IF NOT EXISTS idx_news_vertical ON news(vertical);
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_source_url ON news(source_url);

-- Full-text search for news
CREATE INDEX IF NOT EXISTS idx_news_fts ON news 
    USING GIN (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(content, '')));

-- ===========================================
-- Submissions Table
-- ===========================================
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL,
    submitter_email TEXT,
    notes TEXT,
    
    -- Processing status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'approved', 'rejected', 'failed')),
    
    -- Link to created tool (if approved)
    tool_id UUID REFERENCES tools(id),
    
    -- Processing metadata
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Indexes for submissions
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at DESC);

-- ===========================================
-- Newsletter Subscribers Table
-- ===========================================
CREATE TABLE IF NOT EXISTS subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    source TEXT DEFAULT 'website',
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Preferences
    preferences JSONB DEFAULT '{}',
    
    -- Timestamps
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ
);

-- Indexes for subscribers
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
CREATE INDEX IF NOT EXISTS idx_subscribers_active ON subscribers(is_active);

-- ===========================================
-- Podcast Shows Table
-- ===========================================
CREATE TABLE IF NOT EXISTS podcast_shows (
    id TEXT PRIMARY KEY, -- slug-based ID
    title TEXT NOT NULL,
    description TEXT,
    feed_url TEXT UNIQUE NOT NULL,
    website_url TEXT,
    
    -- Media
    image_url TEXT,
    
    -- Metadata
    author TEXT,
    categories TEXT[] DEFAULT '{}',
    episode_count INT DEFAULT 0,
    
    -- Timestamps
    latest_episode_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- Podcast Episodes Table
-- ===========================================
CREATE TABLE IF NOT EXISTS podcast_episodes (
    id TEXT PRIMARY KEY, -- Generated from show + episode
    show_id TEXT REFERENCES podcast_shows(id),
    
    title TEXT NOT NULL,
    description TEXT,
    audio_url TEXT NOT NULL,
    episode_url TEXT,
    
    -- Duration in seconds
    duration_seconds INT,
    
    -- Extracted info
    guest_names TEXT[] DEFAULT '{}',
    topics TEXT[] DEFAULT '{}',
    
    -- Timestamps
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for podcasts
CREATE INDEX IF NOT EXISTS idx_podcast_episodes_show ON podcast_episodes(show_id);
CREATE INDEX IF NOT EXISTS idx_podcast_episodes_published ON podcast_episodes(published_at DESC);

-- ===========================================
-- Pipeline Runs Table (for tracking)
-- ===========================================
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_name TEXT NOT NULL,
    status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    
    -- Results
    items_processed INT DEFAULT 0,
    items_created INT DEFAULT 0,
    items_updated INT DEFAULT 0,
    
    -- Error tracking
    error_message TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_task ON pipeline_runs(task_name);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);

-- ===========================================
-- Row Level Security (RLS)
-- ===========================================

-- Enable RLS on all tables
ALTER TABLE tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE news ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE podcast_shows ENABLE ROW LEVEL SECURITY;
ALTER TABLE podcast_episodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;

-- Public read access for approved tools
CREATE POLICY "Public tools are viewable by everyone"
    ON tools FOR SELECT
    USING (status = 'approved');

-- Public read access for news
CREATE POLICY "News is viewable by everyone"
    ON news FOR SELECT
    USING (true);

-- Public read access for podcasts
CREATE POLICY "Podcast shows are viewable by everyone"
    ON podcast_shows FOR SELECT
    USING (true);

CREATE POLICY "Podcast episodes are viewable by everyone"
    ON podcast_episodes FOR SELECT
    USING (true);

-- Service role has full access (for backend)
CREATE POLICY "Service role has full access to tools"
    ON tools FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to news"
    ON news FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to submissions"
    ON submissions FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to subscribers"
    ON subscribers FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to podcast_shows"
    ON podcast_shows FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to podcast_episodes"
    ON podcast_episodes FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to pipeline_runs"
    ON pipeline_runs FOR ALL
    USING (auth.role() = 'service_role');

-- ===========================================
-- Helper Functions
-- ===========================================

-- Function to generate slug from title
CREATE OR REPLACE FUNCTION generate_slug(title TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN lower(regexp_replace(
        regexp_replace(title, '[^a-zA-Z0-9\s-]', '', 'g'),
        '\s+', '-', 'g'
    ));
END;
$$ LANGUAGE plpgsql;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_tools_updated_at
    BEFORE UPDATE ON tools
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_news_updated_at
    BEFORE UPDATE ON news
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_podcast_shows_updated_at
    BEFORE UPDATE ON podcast_shows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===========================================
-- Semantic Search Function
-- ===========================================

-- Function to search tools by semantic similarity
CREATE OR REPLACE FUNCTION search_tools_by_embedding(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    slug TEXT,
    title TEXT,
    description TEXT,
    trust_score INT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        t.slug,
        t.title,
        t.description,
        t.trust_score,
        1 - (t.embedding <=> query_embedding) AS similarity
    FROM tools t
    WHERE t.status = 'approved'
        AND t.embedding IS NOT NULL
        AND 1 - (t.embedding <=> query_embedding) > match_threshold
    ORDER BY t.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ===========================================
-- Stats View
-- ===========================================

CREATE OR REPLACE VIEW platform_stats AS
SELECT
    (SELECT COUNT(*) FROM tools WHERE status = 'approved') AS tools_approved,
    (SELECT COUNT(*) FROM tools WHERE status = 'draft') AS tools_draft,
    (SELECT COUNT(*) FROM news) AS news_count,
    (SELECT COUNT(*) FROM subscribers WHERE is_active = true) AS subscribers_active,
    (SELECT COUNT(*) FROM submissions WHERE status = 'pending') AS submissions_pending,
    (SELECT COUNT(*) FROM podcast_shows) AS podcast_shows,
    (SELECT COUNT(*) FROM podcast_episodes) AS podcast_episodes;

