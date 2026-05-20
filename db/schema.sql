-- GetHired Phase 1 local database schema
-- SQLite
--
-- Gmail ingestion strategy:
-- historyId-first delta sync.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_state (
  source_key TEXT PRIMARY KEY,
  gmail_user_id TEXT NOT NULL DEFAULT 'me',
  gmail_label_name TEXT NOT NULL,
  gmail_label_id TEXT,
  last_history_id TEXT NOT NULL,
  last_synced_at TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sync_state_label_name
  ON sync_state(gmail_label_name);

CREATE TABLE IF NOT EXISTS gmail_messages (
  gmail_message_id TEXT PRIMARY KEY,
  gmail_thread_id TEXT NOT NULL,
  internal_ts TEXT NOT NULL,
  history_id TEXT NOT NULL,
  subject TEXT,
  from_email TEXT,
  snippet TEXT,
  raw_payload_json TEXT,
  first_seen_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  parse_status TEXT NOT NULL CHECK (
    parse_status IN ('pending', 'parsed', 'error', 'skipped')
  ),
  parse_error TEXT
);

CREATE INDEX IF NOT EXISTS idx_gmail_messages_history_id
  ON gmail_messages(history_id);

CREATE INDEX IF NOT EXISTS idx_gmail_messages_internal_ts
  ON gmail_messages(internal_ts);

CREATE INDEX IF NOT EXISTS idx_gmail_messages_parse_status
  ON gmail_messages(parse_status);

CREATE TABLE IF NOT EXISTS parsed_jobs (
  id TEXT PRIMARY KEY,
  source_message_id TEXT NOT NULL REFERENCES gmail_messages(gmail_message_id),
  source_type TEXT NOT NULL,
  title TEXT,
  company TEXT,
  location TEXT,
  url TEXT,
  raw_text TEXT,
  detected_at TEXT NOT NULL,
  posted_at TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_parsed_jobs_source_message
  ON parsed_jobs(source_message_id);

CREATE INDEX IF NOT EXISTS idx_parsed_jobs_detected_at
  ON parsed_jobs(detected_at);

CREATE INDEX IF NOT EXISTS idx_parsed_jobs_url
  ON parsed_jobs(url);

CREATE TABLE IF NOT EXISTS job_postings (
  id TEXT PRIMARY KEY,
  canonical_key TEXT NOT NULL UNIQUE,
  title TEXT,
  company TEXT,
  location TEXT,
  source TEXT,
  source_type TEXT,
  url TEXT,
  apply_url TEXT,
  posted_at TEXT,
  detected_at TEXT NOT NULL,
  description TEXT,
  raw_text TEXT,
  score REAL,
  score_reason TEXT,
  status TEXT NOT NULL DEFAULT 'new' CHECK (
    status IN ('new', 'reviewing', 'applied', 'ignored')
  ),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_job_postings_detected_at
  ON job_postings(detected_at);

CREATE INDEX IF NOT EXISTS idx_job_postings_status
  ON job_postings(status);

CREATE INDEX IF NOT EXISTS idx_job_postings_company
  ON job_postings(company);

CREATE INDEX IF NOT EXISTS idx_job_postings_title
  ON job_postings(title);

CREATE INDEX IF NOT EXISTS idx_job_postings_location
  ON job_postings(location);

CREATE TABLE IF NOT EXISTS job_posting_sources (
  id TEXT PRIMARY KEY,
  job_posting_id TEXT NOT NULL REFERENCES job_postings(id),
  parsed_job_id TEXT NOT NULL REFERENCES parsed_jobs(id),
  source_message_id TEXT NOT NULL REFERENCES gmail_messages(gmail_message_id),
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_job_posting_sources_job_posting
  ON job_posting_sources(job_posting_id);

CREATE INDEX IF NOT EXISTS idx_job_posting_sources_source_message
  ON job_posting_sources(source_message_id);
