import pytest

from gethired.google_alerts import generate_google_alert_queries
from gethired.search_profile import SearchProfile


def test_generates_default_ats_title_location_queries():
    profile = SearchProfile(
        profile_name="ML Germany",
        job_titles=("Data Scientist", "Machine Learning Engineer"),
        priority_keywords=("LLM",),
        locations=("Germany",),
    )

    queries = generate_google_alert_queries(profile)

    assert queries == [
        'site:boards.greenhouse.io "Data Scientist" Germany',
        'site:boards.greenhouse.io "Machine Learning Engineer" Germany',
        'site:jobs.lever.co "Data Scientist" Germany',
        'site:jobs.lever.co "Machine Learning Engineer" Germany',
        'site:jobs.personio.de "Data Scientist" Germany',
        'site:jobs.personio.de "Machine Learning Engineer" Germany',
        'site:jobs.smartrecruiters.com "Data Scientist" Germany',
        'site:jobs.smartrecruiters.com "Machine Learning Engineer" Germany',
        'site:teamtailor.com "Data Scientist" Germany',
        'site:teamtailor.com "Machine Learning Engineer" Germany',
    ]


def test_priority_keyword_queries_are_optional():
    profile = SearchProfile(
        profile_name="ML Germany",
        job_titles=("AI Engineer",),
        priority_keywords=("RAG",),
        locations=("Germany",),
    )

    queries = generate_google_alert_queries(
        profile,
        ats_domains=("jobs.lever.co",),
        include_priority_keywords=True,
    )

    assert queries == [
        'site:jobs.lever.co "AI Engineer" Germany',
        'site:jobs.lever.co "RAG" Germany',
    ]


def test_deduplicates_queries_while_preserving_order():
    profile = SearchProfile(
        profile_name="ML Germany",
        job_titles=("Data Scientist", "Data Scientist"),
        locations=("Germany",),
    )

    queries = generate_google_alert_queries(
        profile,
        ats_domains=("jobs.lever.co", "jobs.lever.co"),
    )

    assert queries == ['site:jobs.lever.co "Data Scientist" Germany']


def test_limits_query_count_to_avoid_query_explosion():
    profile = SearchProfile(
        profile_name="ML Germany",
        job_titles=("Data Scientist", "ML Engineer"),
        locations=("Germany", "Berlin"),
    )

    queries = generate_google_alert_queries(
        profile,
        ats_domains=("jobs.lever.co", "jobs.personio.de"),
        max_queries=3,
    )

    assert len(queries) == 3


def test_rejects_invalid_max_queries():
    profile = SearchProfile(
        profile_name="ML Germany",
        job_titles=("Data Scientist",),
        locations=("Germany",),
    )

    with pytest.raises(ValueError, match="max_queries"):
        generate_google_alert_queries(profile, max_queries=0)
