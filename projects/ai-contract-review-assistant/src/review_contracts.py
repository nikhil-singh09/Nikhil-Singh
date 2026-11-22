"""Rule-based contract field extraction with evidence; not legal advice."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import csv

PATTERNS = {
    "effective_date": r"Effective Date\s*:\s*([^\n.]+)",
    "termination": r"(Either party may terminate[^\n.]*[.]?)",
    "governing_law": r"(?:Governing Law\s*:\s*)([^\n.]+)",
    "liability_cap": r"(Each party's aggregate liability[^\n.]*[.]?)",
    "confidentiality": r"(Each party must protect[^\n.]*[.]?)",
}


def extract_fields(text: str) -> dict:
    results = {}
    for field, pattern in PATTERNS.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        results[field] = {
            "value": match.group(1).strip() if match else None,
            "evidence": match.group(0).strip() if match else None,
            "status": "found_rule_match" if match else "not_found",
        }
    party_match = re.search(
        r"entered into by\s+(.+?)\s+\(Customer\)\s+and\s+(.+?)\s+\(Provider\)",
        text, flags=re.IGNORECASE,
    )
    results["parties"] = {
        "value": {"customer": party_match.group(1), "provider": party_match.group(2)}
        if party_match else None,
        "evidence": party_match.group(0) if party_match else None,
        "status": "found_rule_match" if party_match else "not_found",
    }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/contracts"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    records = []
    for file in sorted(args.input.glob("*.txt")):
        text = file.read_text(encoding="utf-8")
        records.append({"source_file": file.name, "fields": extract_fields(text)})

    (args.output / "contract_reviews.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (args.output / "review_register.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_file", "field", "value", "status", "evidence"])
        writer.writeheader()
        for record in records:
            for field, item in record["fields"].items():
                writer.writerow({
                    "source_file": record["source_file"], "field": field,
                    "value": json.dumps(item["value"], ensure_ascii=False),
                    "status": item["status"], "evidence": item["evidence"],
                })
    print(f"Reviewed {len(records)} text document(s); outputs saved to {args.output.resolve()}")


if __name__ == "__main__":
    main()
