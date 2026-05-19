"""Small local UI for manually reviewing generated Google Alert queries."""

from __future__ import annotations

import argparse
import html
import logging
from dataclasses import replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from gethired.google_alerts import generate_google_alert_queries
from gethired.search_profile import SearchProfile, load_search_profile

LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_MAX_QUERIES = 50


def build_page(
    profile: SearchProfile,
    *,
    queries: list[str],
    include_priority_keywords: bool,
    max_queries: int,
    error_message: str | None = None,
) -> str:
    """Build the local query review page."""
    escaped_queries = html.escape("\n".join(queries))
    profile_summary = _build_profile_summary(profile)
    checked = " checked" if include_priority_keywords else ""
    escaped_error = html.escape(error_message) if error_message else ""
    error_block = (
        f'<div class="notice notice-error">{escaped_error}</div>' if escaped_error else ""
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GetHired</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f4ee;
      --panel: #ffffff;
      --text: #202124;
      --muted: #5f6368;
      --line: #d8d3c8;
      --accent: #155e75;
      --accent-dark: #0f4758;
      --surface: #f9fafb;
      --warn-bg: #fff4e5;
      --warn-text: #7a3b00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    .shell {{
      width: min(1120px, calc(100vw - 32px));
      margin: 0 auto;
    }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      min-height: 72px;
      gap: 16px;
    }}
    .brand {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 0;
    }}
    .subtitle {{
      color: var(--muted);
      font-size: 14px;
    }}
    main {{
      padding: 28px 0 40px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 24px;
      align-items: start;
    }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px;
    }}
    h2 {{
      margin: 0;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .section-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 16px;
      margin: -2px 0 18px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--line);
    }}
    .section-note {{
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}
    .control-panel,
    .results-panel {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      padding: 16px;
    }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: end;
      margin: 0;
    }}
    label {{
      display: grid;
      gap: 6px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 600;
    }}
    .check-label {{
      display: flex;
      align-items: center;
      min-height: 38px;
      gap: 10px;
      color: var(--text);
      font-weight: 500;
    }}
    input[type="number"] {{
      width: 120px;
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
      background: #ffffff;
    }}
    button {{
      min-height: 38px;
      border: 0;
      border-radius: 6px;
      padding: 8px 14px;
      background: var(--accent);
      color: #ffffff;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }}
    button:hover {{
      background: var(--accent-dark);
    }}
    textarea {{
      width: 100%;
      min-height: 430px;
      resize: vertical;
      border: 1px solid #c4cbd3;
      border-radius: 8px;
      padding: 14px;
      background: #ffffff;
      font: 14px ui-monospace, SFMono-Regular, Menlo, monospace;
      line-height: 1.55;
    }}
    .profile-fields {{
      display: grid;
      gap: 16px;
    }}
    .profile-field {{
      display: grid;
      gap: 7px;
    }}
    .field-title {{
      color: var(--text);
      font-size: 14px;
      font-weight: 800;
    }}
    .field-note {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 500;
    }}
    .profile-text,
    .profile-input {{
      width: 100%;
      border: 1px solid #c4cbd3;
      border-radius: 8px;
      padding: 10px 12px;
      background: #ffffff;
      font: inherit;
      line-height: 1.5;
    }}
    .profile-text {{
      min-height: 42px;
    }}
    .profile-input {{
      min-height: 92px;
      resize: vertical;
    }}
    .query-count {{
      margin: 0 0 12px;
      color: var(--text);
      font-size: 14px;
      font-weight: 700;
    }}
    .query-hint {{
      margin: -6px 0 14px;
      color: var(--muted);
      font-size: 14px;
    }}
    .notice {{
      margin-bottom: 16px;
      border-radius: 8px;
      padding: 12px 14px;
      font-size: 14px;
    }}
    .notice-error {{
      background: var(--warn-bg);
      color: var(--warn-text);
      border: 1px solid #f2c078;
    }}
    @media (max-width: 820px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .section-header {{
        align-items: flex-start;
        flex-direction: column;
      }}
      .topbar {{
        align-items: flex-start;
        flex-direction: column;
        padding: 16px 0;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="shell topbar">
      <div class="brand">
        <h1>GetHired</h1>
        <div class="subtitle">A modular job discovery system for finding, organizing, scoring, and tracking fresh opportunities.</div>
      </div>
    </div>
  </header>
  <main class="shell">
    <div class="layout">
      <section aria-labelledby="profile-heading">
        <div class="section-header">
          <h2 id="profile-heading">Search Profile</h2>
          <span class="section-note">Inputs used to generate Google Alert queries</span>
        </div>
        {profile_summary}
      </section>
      <section aria-labelledby="queries-heading">
        <div class="section-header">
          <h2 id="queries-heading">Generated Queries</h2>
          <span class="section-note">Manual Google Alerts setup</span>
        </div>
        {error_block}
        <div class="control-panel">
          <form id="query-form" method="post" class="controls">
            <label class="check-label">
              <input type="checkbox" name="include_priority_keywords" value="1"{checked}>
              Include priority keywords
            </label>
            <label>
              Max queries
              <input type="number" name="max_queries" min="1" max="200" value="{max_queries}">
            </label>
            <button type="submit">Generate</button>
          </form>
        </div>
        <div class="results-panel" style="margin-top: 16px;">
          <p class="query-count">{len(queries)} queries ready to copy into Google Alerts.</p>
          <p class="query-hint">Copy these lines into Google Alerts manually. Keep location terms in the query, set Region to Any region / 不限地區, and deliver alerts to Gmail.</p>
          <textarea readonly>{escaped_queries}</textarea>
        </div>
      </section>
    </div>
  </main>
</body>
</html>"""


def _build_profile_summary(profile: SearchProfile) -> str:
    fields = [
        _build_text_input(
            "Profile",
            "profile_name",
            profile.profile_name,
            "Human-readable name for this search profile.",
        ),
        _build_textarea(
            "Job titles",
            "job_titles",
            profile.job_titles,
            "One per line or comma separated.",
        ),
        _build_textarea(
            "Locations",
            "locations",
            profile.locations,
            "One per line or comma separated.",
        ),
        _build_textarea(
            "Keywords",
            "keywords",
            profile.keywords,
            "Useful later for scoring and matching.",
        ),
        _build_textarea(
            "Priority keywords",
            "priority_keywords",
            profile.priority_keywords,
            "Optional extra query terms.",
        ),
        _build_textarea(
            "Excluded keywords",
            "exclude_keywords",
            profile.exclude_keywords,
            "Used later for filtering and scoring penalties.",
        ),
    ]
    return f'<div class="profile-fields">{"".join(fields)}</div>'


def _build_text_input(label: str, name: str, value: str, note: str) -> str:
    return (
        '<div class="profile-field">'
        f'<label class="field-title" for="{name}">{html.escape(label)}</label>'
        f'<span class="field-note">{html.escape(note)}</span>'
        f'<input class="profile-text" id="{name}" name="{name}" '
        f'form="query-form" value="{html.escape(value)}">'
        "</div>"
    )


def _build_textarea(
    label: str,
    name: str,
    values: tuple[str, ...],
    note: str,
) -> str:
    value = html.escape("\n".join(values))
    return (
        '<div class="profile-field">'
        f'<label class="field-title" for="{name}">{html.escape(label)}</label>'
        f'<span class="field-note">{html.escape(note)}</span>'
        f'<textarea class="profile-input" id="{name}" name="{name}" '
        f'form="query-form">{value}</textarea>'
        "</div>"
    )


def create_handler(profile_path: str | Path) -> type[BaseHTTPRequestHandler]:
    """Create a request handler bound to one Search Profile file."""

    class GetHiredRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self._render(include_priority_keywords=False, max_queries=DEFAULT_MAX_QUERIES)

        def do_POST(self) -> None:
            content_length = int(self.headers.get("Content-Length", "0"))
            form_data = self.rfile.read(content_length).decode("utf-8")
            parsed_form = parse_qs(form_data)
            loaded_profile = load_search_profile(profile_path)
            profile, profile_error = _profile_from_form(loaded_profile, parsed_form)
            include_priority_keywords = (
                parsed_form.get("include_priority_keywords", ["0"])[0] == "1"
            )
            max_queries, error_message = _parse_max_queries(
                parsed_form.get("max_queries", [str(DEFAULT_MAX_QUERIES)])[0]
            )
            error_message = profile_error or error_message
            self._render(
                profile=profile,
                include_priority_keywords=include_priority_keywords,
                max_queries=max_queries,
                error_message=error_message,
            )

        def log_message(self, format: str, *args: Any) -> None:
            LOGGER.info("UI request: " + format, *args)

        def _render(
            self,
            *,
            profile: SearchProfile | None = None,
            include_priority_keywords: bool,
            max_queries: int,
            error_message: str | None = None,
        ) -> None:
            try:
                if profile is None:
                    profile = load_search_profile(profile_path)
                queries = generate_google_alert_queries(
                    profile,
                    include_priority_keywords=include_priority_keywords,
                    max_queries=max_queries,
                )
                page = build_page(
                    profile,
                    queries=queries,
                    include_priority_keywords=include_priority_keywords,
                    max_queries=max_queries,
                    error_message=error_message,
                )
                self._send_html(page, HTTPStatus.OK)
            except (FileNotFoundError, ValueError) as exc:
                LOGGER.error("Could not render local UI: %s", exc)
                self._send_html(
                    f"<h1>GetHired</h1><p>{html.escape(str(exc))}</p>",
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        def _send_html(self, page: str, status: HTTPStatus) -> None:
            encoded_page = page.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded_page)))
            self.end_headers()
            self.wfile.write(encoded_page)

    return GetHiredRequestHandler


def _parse_max_queries(value: str) -> tuple[int, str | None]:
    try:
        parsed_value = int(value)
    except ValueError:
        return DEFAULT_MAX_QUERIES, "Max queries must be a number. Using 50."

    if parsed_value < 1:
        return DEFAULT_MAX_QUERIES, "Max queries must be at least 1. Using 50."
    if parsed_value > 200:
        return 200, "Max queries was capped at 200."
    return parsed_value, None


def _parse_list_input(value: str) -> tuple[tuple[str, ...], str | None]:
    normalized_value = value.replace("\r\n", "\n").replace(",", "\n")
    items = tuple(item.strip() for item in normalized_value.split("\n") if item.strip())
    if not items:
        return (), "Job titles must include at least one value."
    return items, None


def _parse_optional_list_input(value: str) -> tuple[str, ...]:
    normalized_value = value.replace("\r\n", "\n").replace(",", "\n")
    return tuple(item.strip() for item in normalized_value.split("\n") if item.strip())


def _profile_from_form(
    base_profile: SearchProfile,
    parsed_form: dict[str, list[str]],
) -> tuple[SearchProfile, str | None]:
    profile_name = parsed_form.get("profile_name", [base_profile.profile_name])[0].strip()
    if not profile_name:
        return base_profile, "Profile name must include a value."

    job_titles, job_title_error = _parse_list_input(
        parsed_form.get("job_titles", [""])[0]
    )
    if job_title_error:
        return base_profile, job_title_error

    locations, location_error = _parse_list_input(parsed_form.get("locations", [""])[0])
    if location_error:
        return base_profile, "Locations must include at least one value."

    return (
        replace(
            base_profile,
            profile_name=profile_name,
            job_titles=job_titles,
            locations=locations,
            keywords=_parse_optional_list_input(parsed_form.get("keywords", [""])[0]),
            priority_keywords=_parse_optional_list_input(
                parsed_form.get("priority_keywords", [""])[0]
            ),
            exclude_keywords=_parse_optional_list_input(
                parsed_form.get("exclude_keywords", [""])[0]
            ),
        ),
        None,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the GetHired local UI.")
    parser.add_argument("profile_path", help="Path to a Search Profile JSON file.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    server = HTTPServer((args.host, args.port), create_handler(args.profile_path))
    LOGGER.info("GetHired local UI running at http://%s:%s", args.host, args.port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("GetHired local UI stopped")
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
