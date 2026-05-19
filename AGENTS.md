# Project Agent Rules

This repository uses STRICT APPROVAL MODE.

These rules apply to all AI coding agents working in this repository.

If these rules conflict with a user prompt, follow the stricter rule unless the user explicitly overrides it in writing.

---

## 1. Core Workflow

You may freely read and search the entire repository.

You must not modify, create, rename, delete, or move any file unless the user explicitly says:

```text
APPLY DIFF
```

Before proposing any modification, you must provide:

- A short implementation plan
- Exact files to be changed or created
- The reason for each change
- Unified diffs for each file

After the user says `APPLY DIFF`:

- Apply only the approved diffs
- Do not introduce additional improvements
- Do not refactor unrelated code
- Do not rename files unless explicitly approved
- Do not change database schema unless explicitly approved
- Run the test command:

```bash
python -m pytest -q
```

- Report the full test results

If tests fail:

- Analyze the failure
- Provide new unified diffs
- Wait again for `APPLY DIFF`

---

## 2. Phase 1 Project Scope

The current approved project scope is Phase 1 only.

Phase 1 includes:

- Local execution on the user's Mac
- Gmail job alert emails
- Google Alert emails
- Search Profile UI or config
- Google Alert query generation
- Job normalization
- Deduplication
- Rule-based scoring
- Local output or dashboard
- Optional local scheduler

Phase 1 does not include:

- Search API
- SerpApi
- Brave Search API
- Tavily
- Serper
- active ATS-wide crawling
- direct LinkedIn scraping
- direct XING scraping
- direct StepStone scraping
- direct Indeed scraping
- CAPTCHA solving
- anti-bot bypassing
- login scraping
- cloud deployment

Do not add out-of-scope features unless explicitly requested.

---

## 3. Test Policy

If relevant tests already exist:

- Update them as part of the proposed change.

If no relevant tests exist:

- First propose a minimal new test.
- Prefer controller-level, service-level, parser-level, or unit-level tests.
- Avoid adding heavy test dependencies unless clearly justified.
- If adding tests would introduce major new dependencies, explicitly justify skipping tests and propose a lightweight verification strategy.

Never modify or create test files without `APPLY DIFF` approval.

---

## 4. Documentation Policy

For user-facing behavior, architecture, setup, commands, or configuration changes:

- Propose README updates together with the code change.
- Keep README explanations clear enough for:
  - the project owner's future self
  - another developer
  - a recruiter or hiring manager reviewing the project

Documentation changes also require `APPLY DIFF`.

---

## 5. Clean Code Requirements

Keep changes minimal, modular, and maintainable.

Prefer:

- Low coupling
- High cohesion
- Clear separation of concerns
- Small functions
- Explicit interfaces
- Easy-to-extend email parsers
- Easy-to-extend source adapters
- No duplicated business logic
- No hard-coded search terms when they should come from Search Profiles
- No hidden side effects
- No unnecessary architecture changes

Always prefer minimal, task-focused changes over broad refactors.

---

## 6. Error Handling Requirements

Use proper error handling.

Do not use:

```python
except:
    pass
```

Do not use broad exception handling unless there is a clear reason.

Prefer:

- Catching specific exception types
- Logging errors with useful context
- Returning meaningful error states to the caller or UI
- Letting one malformed email fail gracefully without crashing the entire discovery pipeline
- Continuing other independent emails or sources when one item fails

If broad exception handling is unavoidable, explain why in the implementation plan and log the exception.

---

## 7. Logging Requirements

Use logging instead of `print`.

Prefer Python standard logging unless the project already has a better setup.

Log useful pipeline events, such as:

- Search profile loaded
- Google Alert queries generated
- Gmail scan started
- Gmail scan failed
- Emails discovered
- Emails parsed
- Jobs discovered
- Jobs normalized
- Duplicates removed
- Scoring completed
- Notification prepared

Do not log sensitive data, including:

- API keys
- tokens
- credentials
- full email contents
- private user data

---

## 8. Job Discovery Safety Rules

This project is for stable job discovery, not anti-bot bypassing.

Do not implement:

- CAPTCHA solving
- anti-bot bypassing
- login scraping
- scraping protected LinkedIn, XING, StepStone, or Indeed pages
- credential hardcoding
- storing API keys in source code
- destructive automation against job boards

LinkedIn, XING, StepStone, and Indeed should be handled through:

- Gmail job alert emails
- user-provided exported data
- public links where allowed

Google Alerts should be handled through:

- Google Alert emails received in Gmail
- user-generated Google Alert query suggestions

Do not call Search APIs in Phase 1.

Do not bypass access controls.

---

## 9. Search Profile and Google Alert Query Rules

Search terms must come from Search Profiles whenever possible.

A Search Profile may include:

- profile_name
- job_titles
- keywords
- priority_keywords
- locations
- exclude_keywords
- enabled_email_sources
- google_alert_queries
- scan_frequency_minutes
- notification_score_threshold

Generated Google Alert queries may use ATS domains such as:

- boards.greenhouse.io
- jobs.lever.co
- jobs.personio.de
- jobs.smartrecruiters.com
- teamtailor.com

Avoid query explosion.

Prefer generating:

- ATS domain × job_title × location
- selected priority keyword queries only

Do not generate every possible combination of all titles, locations, domains, and keywords unless explicitly requested.

Generated queries are for the user to manually copy into Google Alerts in Phase 1.

Do not call Google Search, SerpApi, Brave, Tavily, Serper, or any other Search API in Phase 1.

---

## 10. Source and Parser Architecture

Keep email discovery, parsing, normalization, deduplication, and scoring separate.

Sources discover raw inputs:

- GmailAlertSource

Email parsers extract structured job candidates from messages:

- LinkedInAlertEmailParser
- XingAlertEmailParser
- StepStoneAlertEmailParser
- IndeedAlertEmailParser
- GoogleAlertEmailParser
- GenericJobAlertEmailParser

All parsed jobs should normalize into a common JobPosting schema.

The schema should distinguish:

- posted_at: date shown by the source, if available
- detected_at: first time this system discovered the job

Do not add ATS crawling parsers in Phase 1 unless explicitly requested.

---

## 11. Local Hosting and Scheduling Rules

The project should run locally on the user's Mac in Phase 1.

Do not add cloud deployment in Phase 1.

A local UI may run at:

```text
http://localhost:8000
```

or another clearly documented local port.

Default scan settings:

- Gmail job alerts: every 30 minutes
- Google Alert emails: every 30 minutes
- Daily cleanup / re-score: once per day

The scheduler must be optional and easy to disable.

Manual scan commands or UI buttons must work even if the scheduler is disabled.

---

## 12. Git and File Safety

Do not run destructive git commands.

Do not run:

```bash
git reset --hard
git clean -fd
git push --force
rm -rf
```

Do not delete files.

Do not rename files unless required and explicitly approved.

Do not change database schema unless explicitly requested.

Do not install new dependencies without explaining why and receiving approval.

---

## 13. Command Safety

Before running commands that may modify files, explain the command and wait for approval.

Safe read-only commands are allowed, such as:

```bash
ls
find
grep
rg
cat
sed -n
python -m pytest -q
```

Do not run formatters, migrations, package installers, or code generators unless explicitly approved.

Examples requiring approval:

```bash
black .
ruff --fix .
npm install
pip install
alembic upgrade head
python manage.py migrate
```

---

## 14. Final Response Requirements

When reporting work, include:

- What was inspected
- What is proposed
- Files involved
- Risks or tradeoffs
- Test plan
- Whether any files were modified

If no files were modified, say so clearly.

If files were modified after `APPLY DIFF`, include:

- Changed files
- Test command run
- Full test result summary
- Any remaining issues
