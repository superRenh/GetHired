# GetHired

GetHired is a modular job discovery system for collecting, organizing, scoring, and tracking fresh career opportunities across multiple sources.

The long-term goal is to help job seekers discover relevant opportunities earlier than manual job board checking, while keeping the system transparent, local-first, and respectful of source platform rules.

## Project Vision

GetHired is designed as a general job discovery system, not a tool tied to one country, one job category, or one source type.

Future versions should be able to collect job-like signals from multiple allowed sources, normalize them into a common schema, remove duplicates, score them with clear rules, and present them in a local review workflow.

## Phase 1 Scope

Phase 1 runs locally on a Mac and focuses on:

- Gmail job alert emails
- Google Alert emails
- Search Profile config
- Google Alert query generation
- Job normalization
- Deduplication
- Rule-based scoring
- Local dashboard or output
- Optional local scheduler

The first vertical slice in this repository only implements Search Profile config and Google Alert query generation.

## Phase 1 Non-Goals

Phase 1 intentionally does not include:

- Search APIs
- SerpApi
- Brave Search API
- Tavily
- Serper
- Active ATS-wide crawling
- Direct LinkedIn scraping
- Direct XING scraping
- Direct StepStone scraping
- Direct Indeed scraping
- CAPTCHA solving
- Anti-bot bypassing
- Login scraping
- Cloud deployment

## Job Discovery Safety

GetHired avoids direct scraping of protected job boards because the project is meant to support stable, respectful job discovery rather than bypass access controls or platform defenses.

For Phase 1, LinkedIn, XING, StepStone, and Indeed should be handled through job alert emails, user-provided exported data, or public links where allowed. Google Alerts are handled through queries that the user manually creates in Google Alerts and through alert emails received later in Gmail.

## Search Profiles

A Search Profile describes what kind of jobs to look for. The current implementation uses a simple JSON config file.

Example:

```json
{
  "profile_name": "ML Data AI Germany",
  "job_titles": [
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer"
  ],
  "keywords": [
    "Python",
    "SQL",
    "Azure"
  ],
  "priority_keywords": [
    "LLM",
    "RAG",
    "LangChain"
  ],
  "locations": [
    "Germany"
  ],
  "exclude_keywords": [
    "internship",
    "unpaid"
  ],
  "enabled_email_sources": [
    "google_alerts",
    "gmail_job_alerts"
  ],
  "google_alert_queries": [],
  "scan_frequency_minutes": 30,
  "notification_score_threshold": 70
}
```

See `config/search_profile.example.json` for a ready-to-edit example.

## Google Alert Query Generation

The Google Alert query generator creates search strings that can be manually copied into Google Alerts.

By default, it generates conservative combinations using:

- ATS domain
- Job title
- Location

Default ATS domains:

- `boards.greenhouse.io`
- `jobs.lever.co`
- `jobs.personio.de`
- `jobs.smartrecruiters.com`
- `teamtailor.com`

Example generated query:

```text
site:boards.greenhouse.io "Data Scientist" Germany
```

The generator does not call Google Search, Google Alerts, SerpApi, Brave, Tavily, Serper, or any other Search API.

## Generate Google Alert Queries

Create a local virtual environment:

```bash
python3 -m venv .venv
```

Install dependencies:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Run:

```bash
.venv/bin/python -m gethired.google_alerts config/search_profile.example.json
```

To also generate selected priority keyword queries:

```bash
.venv/bin/python -m gethired.google_alerts config/search_profile.example.json --include-priority-keywords
```

Copy the generated lines manually into Google Alerts.

## Manual Google Alerts Settings

When creating Google Alerts manually, keep location terms such as `Germany`, `Berlin`, `Munich`, or `Remote` inside the query text itself.

Do not use the Google Alerts Region filter for Germany during Phase 1 testing. Manual testing showed that Google Alerts preview may return no results when Region is set to Germany, even for ATS job pages whose content includes German job locations.

Recommended Google Alerts settings:

- Frequency: As-it-happens or At most once a day
- Sources: Automatic or Web
- Language: Any language / 不限語言
- Region: Any region / 不限地區
- How many: All results during testing, then Best results if emails become too noisy
- Deliver to: Gmail

GetHired does not call Search APIs and does not automate Google Alerts creation.

## Run The Local UI

The current UI is a small local page for manually reviewing and copying generated Google Alert queries.

Start it with:

```bash
.venv/bin/python -m gethired.web_app config/search_profile.example.json
```

Then open:

```text
http://localhost:8000
```

This UI does not save changes yet. It reads the Search Profile JSON file, generates Google Alert queries, and gives you a copy-friendly text area.

The UI has two tabs:

- Search Profile: edit query inputs and generate Google Alert queries.
- Job Listings: preview the job review table using local fixture data.

The Job Listings tab does not connect to Gmail yet. The planned Gmail label is `GetHired/Job Alerts`; future Gmail integration should read that label with Gmail API read-only access and parse job alert emails into this table.

## Run Tests

After creating the virtual environment and installing dependencies, run:

```bash
.venv/bin/python -m pytest -q
```

If your shell has a `python` command mapped to the project environment, this also works:

```bash
python -m pytest -q
```

## Local Database Plan (Phase 1)

GetHired Phase 1 uses a local SQLite database. The schema is defined in:

- `db/schema.sql`

Core tables:

- `sync_state`: Gmail source cursor state (`last_history_id`) per label/source.
- `gmail_messages`: raw message metadata discovered from Gmail delta sync.
- `parsed_jobs`: parser output candidates extracted from Gmail messages.
- `job_postings`: canonical deduplicated jobs for UI review and scoring.
- `job_posting_sources`: provenance links from canonical jobs back to parsed jobs/messages.

### Gmail Delta Sync Rule

Phase 1 follows a strict `historyId`-first delta model:

1. Read `last_history_id` from `sync_state` for `gmail_label_name = GetHired/Job Alerts`.
2. Call Gmail History API with `startHistoryId = last_history_id`.
3. Fetch changed message IDs and upsert `gmail_messages`.
4. Parse changed messages into `parsed_jobs`.
5. Upsert deduplicated rows into `job_postings`.
6. Persist the latest history ID back to `sync_state`.

No mitigation fallback path is defined in this phase for expired history IDs. If Gmail returns an invalid/expired `startHistoryId`, the scan should fail fast and require explicit re-bootstrap of the cursor.

### Planned Job List Filters

The DB layout is designed to support:

- Time filters: `1 day`, `3 days`, `1 week`, custom date interval.
- Search filters: title, company, location.
- Status filters: `new`, `reviewing`, `applied`, `ignored`.

Time filters should use `job_postings.detected_at` as the default recency field.

## Current Limitations

- No Gmail API integration yet.
- No email parsing yet.
- No job normalization, deduplication, or scoring yet.
- No dashboard yet.
- No scheduler yet.
- Search profiles are JSON files only.

## Future Improvements

- Gmail job alert source
- Google Alert email parser
- LinkedIn, XING, StepStone, Indeed alert email parsers
- Common `JobPosting` schema
- Deduplication
- Rule-based scoring
- Local dashboard
- Optional local scheduler
