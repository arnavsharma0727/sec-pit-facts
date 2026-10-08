from datetime import date

from sec_pit_facts.facts import latest_filed_revision, select_facts_as_of


def test_cutoff_and_revision_selection_preserve_duration_keys():
    payload = {"facts": {"us-gaap": {"Revenue": {"label": "Revenue", "units": {"USD": [
        {"val": 10, "start": "2023-01-01", "end": "2023-03-31", "filed": "2023-05-01", "form": "10-Q", "accn": "a"},
        {"val": 11, "start": "2023-01-01", "end": "2023-03-31", "filed": "2023-08-01", "form": "10-Q", "accn": "b"},
        {"val": 30, "start": "2023-01-01", "end": "2023-09-30", "filed": "2023-11-01", "form": "10-Q", "accn": "c"},
        {"val": 40, "start": "2023-01-01", "end": "2023-12-31", "filed": "2024-02-01", "form": "10-K", "accn": "d"},
    ]}}}}}
    available = select_facts_as_of(payload, ["Revenue"], date(2023, 9, 1))
    selected = latest_filed_revision(available)
    assert [(r["value"], r["start"], r["end"], r["accession"]) for r in selected] == [
        (11, "2023-01-01", "2023-03-31", "b")
    ]


def test_missing_concept_is_empty():
    assert select_facts_as_of({"facts": {"us-gaap": {}}}, ["Unknown"], date(2024, 1, 1)) == []
