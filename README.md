# SEC point-in-time facts

An as-of-date extractor for SEC company facts. Given a CIK, a cutoff date, and selected US-GAAP concepts, it emits the facts that had actually been filed by that cutoff. It preserves the accession, form, filing date, period, unit, and original value so every output row can be traced to EDGAR.

## Skill demonstrated

- Point-in-time data construction from filings, including late filings and amended/restated facts.
- XBRL period/unit normalization without collapsing distinct quarterly, year-to-date, annual, or instant contexts.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[test]'
export SEC_USER_AGENT='Arnav Sharma arnavsharma0727@gmail.com'
sec-pit-facts --cik 0000320193 --as-of 2024-12-31 --concepts Revenues,NetIncomeLoss --out output
```

The command writes `facts.csv` and `run_manifest.json`. The output is not a valuation recommendation. SEC CompanyFacts aggregates standardized facts and does not expose every dimension or company-specific extension; use the accession URL to inspect the filed statement before relying on an item.

## Source and controls

Source: [SEC EDGAR Company Facts API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces). The SEC requests an identified User-Agent and fair-use rate limits. The tool has no bundled company examples or fabricated observations. Filing time is the availability clock; fiscal period end is not treated as the date the fact became knowable.

## Validation

```bash
pytest
```
