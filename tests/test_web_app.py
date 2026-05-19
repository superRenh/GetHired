from gethired.search_profile import SearchProfile
from gethired.web_app import (
    _parse_list_input,
    _parse_max_queries,
    _profile_from_form,
    build_page,
)


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
