from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import date
from pathlib import Path

import requests

from .facts import latest_filed_revision, select_facts_as_of


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract SEC XBRL company facts available by a filing cutoff date.")
    parser.add_argument("--cik", required=True, help="10-digit SEC Central Index Key")
    parser.add_argument("--as-of", required=True, type=date.fromisoformat, help="YYYY-MM-DD availability cutoff")
    parser.add_argument("--concepts", required=True, help="Comma-separated us-gaap concept names")
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()
    user_agent = os.environ.get("SEC_USER_AGENT")
    if not user_agent:
        parser.error("Set SEC_USER_AGENT to a real name and contact email before calling SEC.gov")
    cik = args.cik.strip().zfill(10)
    if not cik.isdigit() or len(cik) != 10:
        parser.error("CIK must contain at most 10 digits")
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    concepts = [x.strip() for x in args.concepts.split(",") if x.strip()]
    rows = latest_filed_revision(select_facts_as_of(payload, concepts, args.as_of))
    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "facts.csv"
    fields = ["concept", "label", "unit", "value", "start", "end", "filed", "form", "fiscal_year", "fiscal_period", "accession", "frame"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "source_url": url,
        "cik": cik,
        "entity": payload.get("entityName"),
        "as_of": args.as_of.isoformat(),
        "concepts_requested": concepts,
        "rows": len(rows),
        "selection": "latest filed revision by exact concept, unit, start, and end, among observations filed on or before cutoff",
    }
    (args.out / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} point-in-time observations to {csv_path}")
