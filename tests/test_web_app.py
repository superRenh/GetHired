from gethired.search_profile import SearchProfile
from gethired.web_app import (
    _parse_list_input,
    _parse_max_queries,
    _profile_from_form,
    build_page,
    load_job_listings,
    load_job_listings_from_db,
)
from gethired.db import init_db
from gethired.repositories.job_postings_repo import upsert_job_posting


def test_build_page_renders_profile_and_queries():
    profile = SearchProfile(
        profile_name="ML Germany",
        job_titles=("Data Scientist",),
        priority_keywords=("RAG",),
        locations=("Germany",),
        exclude_keywords=("internship",),
    )

    page = build_page(
        profile,
        queries=['site:jobs.lever.co "Data Scientist" Germany'],
        include_priority_keywords=False,
        max_queries=50,
    )

    assert "GetHired" in page
    assert "Search Profile" in page
    assert "Job Listings" in page
    assert 'id="search-profile" class="layout tab-panel"' in page
    assert 'id="job-listings" class="tab-panel"' in page
    assert "ML Germany" in page
    assert 'name="profile_name"' in page
    assert 'name="job_titles"' in page
    assert 'name="locations"' in page
    assert 'name="keywords"' in page
    assert 'name="priority_keywords"' in page
    assert 'name="exclude_keywords"' in page
    assert "Data Scientist" in page
    assert 'site:jobs.lever.co &quot;Data Scientist&quot; Germany' in page
    assert "1 queries ready" in page


def test_build_page_renders_job_listings():
    profile = SearchProfile(
        profile_name="ML Germany",
        job_titles=("Data Scientist",),
        locations=("Germany",),
    )

    page = build_page(
        profile,
        queries=[],
        job_listings=[
            {
                "title": "Machine Learning Engineer",
                "company": "Example GmbH",
                "location": "Berlin, Germany",
                "salary": "N/A",
                "date": "2026-05-19",
                "source": "Google Alerts",
                "url": "https://example.com/job",
                "summary": "Build ML systems.",
                "company_info": "Example company.",
                "description": "Full job description.",
            }
        ],
        include_priority_keywords=False,
        max_queries=50,
    )

    assert "Machine Learning Engineer" in page
    assert "Example GmbH" in page
    assert "Berlin, Germany" in page
    assert "Details" in page
    assert "Link" in page


def test_load_job_listings_reads_fixture(tmp_path):
    fixture = tmp_path / "jobs.json"
    fixture.write_text(
        '[{"title": "Data Scientist", "company": "Example"}]',
        encoding="utf-8",
    )

    assert load_job_listings(path=fixture, db_path=tmp_path / "missing.sqlite3") == [
        {"title": "Data Scientist", "company": "Example"}
    ]


def test_load_job_listings_prefers_db(tmp_path):
    db_path = tmp_path / "gethired.sqlite3"
    init_db(db_path)
    with connect_for_test(db_path) as connection:
        upsert_job_posting(
            connection,
            canonical_key="db-key-1",
            title="DB Role",
            company="DB Company",
            location="Berlin, Germany",
            source="gmail",
            source_type="google_alert",
            url="https://example.com/db-role",
            detected_at="2026-05-20T12:00:00Z",
            description="DB summary",
            raw_text="DB description",
        )

    rows = load_job_listings_from_db(db_path)
    assert len(rows) == 1
    assert rows[0]["title"] == "DB Role"
    assert rows[0]["company"] == "DB Company"


def connect_for_test(db_path):
    from gethired.db import connect_db

    return connect_db(db_path)


def test_build_page_marks_priority_keyword_checkbox_when_enabled():
    profile = SearchProfile(
        profile_name="ML Germany",
        job_titles=("AI Engineer",),
        locations=("Germany",),
    )

    page = build_page(
        profile,
        queries=[],
        include_priority_keywords=True,
        max_queries=10,
    )

    assert 'name="include_priority_keywords" value="1" checked' in page
    assert 'value="10"' in page


def test_parse_max_queries_rejects_non_numeric_values():
    assert _parse_max_queries("many") == (50, "Max queries must be a number. Using 50.")


def test_parse_max_queries_caps_large_values():
    assert _parse_max_queries("250") == (200, "Max queries was capped at 200.")


def test_parse_max_queries_accepts_valid_values():
    assert _parse_max_queries("25") == (25, None)


def test_parse_list_input_accepts_commas_and_newlines():
    assert _parse_list_input("Data Scientist, ML Engineer\nAI Engineer") == (
        ("Data Scientist", "ML Engineer", "AI Engineer"),
        None,
    )


def test_parse_list_input_rejects_empty_values():
    assert _parse_list_input(" , \n ") == (
        (),
        "Job titles must include at least one value.",
    )


def test_profile_from_form_updates_editable_fields():
    profile = SearchProfile(
        profile_name="Original",
        job_titles=("Data Scientist",),
        keywords=("Python",),
        priority_keywords=("RAG",),
        locations=("Germany",),
        exclude_keywords=("internship",),
    )

    updated_profile, error = _profile_from_form(
        profile,
        {
            "profile_name": ["Custom profile"],
            "job_titles": ["Data Analyst\nAI Product Manager"],
            "locations": ["Germany, Remote"],
            "keywords": ["SQL, Python"],
            "priority_keywords": ["LLM\nAgents"],
            "exclude_keywords": ["internship, unpaid"],
        },
    )

    assert error is None
    assert updated_profile.profile_name == "Custom profile"
    assert updated_profile.job_titles == ("Data Analyst", "AI Product Manager")
    assert updated_profile.locations == ("Germany", "Remote")
    assert updated_profile.keywords == ("SQL", "Python")
    assert updated_profile.priority_keywords == ("LLM", "Agents")
    assert updated_profile.exclude_keywords == ("internship", "unpaid")


def test_profile_from_form_keeps_base_profile_when_required_fields_are_empty():
    profile = SearchProfile(
        profile_name="Original",
        job_titles=("Data Scientist",),
        locations=("Germany",),
    )

    updated_profile, error = _profile_from_form(
        profile,
        {"profile_name": [""], "job_titles": ["Data Analyst"], "locations": ["Germany"]},
    )

    assert updated_profile == profile
    assert error == "Profile name must include a value."
