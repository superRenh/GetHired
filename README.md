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

Run:

```bash
python -m gethired.google_alerts config/search_profile.example.json
```

To also generate selected priority keyword queries:

```bash
python -m gethired.google_alerts config/search_profile.example.json --include-priority-keywords
```

Copy the generated lines manually into Google Alerts.

## Run Tests

```bash
python -m pytest -q
```

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
