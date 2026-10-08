from __future__ import annotations

from datetime import date
from typing import Any


def select_facts_as_of(
    payload: dict[str, Any], concepts: list[str], as_of: date
) -> list[dict[str, Any]]:
    """Return filed observations available by ``as_of``, retaining SEC provenance.

    This does not force facts into a single annual/quarterly series. Separate
    period starts, ends, units and forms remain separate observations.
    """
    taxonomies = payload.get("facts", {})
    gaap = taxonomies.get("us-gaap", {})
    output: list[dict[str, Any]] = []
    for concept in concepts:
        definition = gaap.get(concept)
        if definition is None:
            continue
        for unit, observations in definition.get("units", {}).items():
            for item in observations:
                filed = item.get("filed")
                if not filed or date.fromisoformat(filed) > as_of:
                    continue
                output.append({
                    "concept": concept,
                    "label": definition.get("label", concept),
                    "unit": unit,
                    "value": item.get("val"),
                    "start": item.get("start"),
                    "end": item.get("end"),
                    "filed": filed,
                    "form": item.get("form"),
                    "fiscal_year": item.get("fy"),
                    "fiscal_period": item.get("fp"),
                    "accession": item.get("accn"),
                    "frame": item.get("frame"),
                })
    return sorted(output, key=lambda r: (r["concept"], r["unit"], r["end"] or "", r["filed"], r["accession"] or ""))


def latest_filed_revision(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the latest filed revision for each exact concept/period/unit key.

    Exact start/end keys matter: a 3-month quarter and a 9-month year-to-date
    fact ending on the same day are not interchangeable.
    """
    selected: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = (row["concept"], row["unit"], row["start"], row["end"])
        prior = selected.get(key)
        if prior is None or (row["filed"], row["accession"] or "") > (prior["filed"], prior["accession"] or ""):
            selected[key] = row
    return sorted(selected.values(), key=lambda r: (r["concept"], r["unit"], r["end"] or "", r["start"] or ""))
