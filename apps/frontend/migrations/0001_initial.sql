-- Subscribers — the primary list. Status flow:
--   pending -> confirmed -> (unsubscribed | bounced | suppressed)
CREATE TABLE IF NOT EXISTS subscribers (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL CHECK (
    status IN ('pending', 'confirmed', 'unsubscribed', 'bounced', 'suppressed')
  ),
  source TEXT,
  confirm_token TEXT,
  confirm_token_expires INTEGER,
  unsubscribe_token TEXT NOT NULL UNIQUE,
  created_at INTEGER NOT NULL,
  confirmed_at INTEGER,
  unsubscribed_at INTEGER,
  utm_source TEXT,
  utm_campaign TEXT,
  utm_medium TEXT,
  ua TEXT,
  ip_country TEXT
);

CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status);
CREATE INDEX IF NOT EXISTS idx_subscribers_confirm ON subscribers(confirm_token);
CREATE INDEX IF NOT EXISTS idx_subscribers_unsub ON subscribers(unsubscribe_token);
CREATE INDEX IF NOT EXISTS idx_subscribers_created ON subscribers(created_at);

-- Send events — append-only log of every email we sent and the outcome.
CREATE TABLE IF NOT EXISTS send_events (
  id TEXT PRIMARY KEY,
  subscriber_id TEXT NOT NULL,
  email_type TEXT NOT NULL,
  message_id TEXT,
  sent_at INTEGER NOT NULL,
  status TEXT NOT NULL,
  provider TEXT NOT NULL,
  error_code TEXT,
  error_message TEXT,
  FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
);

CREATE INDEX IF NOT EXISTS idx_send_events_subscriber ON send_events(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_send_events_sent ON send_events(sent_at);
CREATE INDEX IF NOT EXISTS idx_send_events_type ON send_events(email_type);
