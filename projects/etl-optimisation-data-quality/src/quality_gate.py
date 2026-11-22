"""Profile, validate and deduplicate a small CSV batch."""
import argparse
import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED = ("client_ref", "invoice_no", "invoice_date", "amount")

def process(source: Path, output: Path) -> dict:
    clean, rejected, seen = [], [], set()
    with source.open(newline="", encoding="utf-8") as handle:
        for line_no, row in enumerate(csv.DictReader(handle), start=2):
            reasons = []
            if any(not row.get(field, "").strip() for field in REQUIRED):
                reasons.append("missing required field")
            try:
                amount = Decimal(row.get("amount", ""))
                if amount < 0:
                    reasons.append("negative amount")
            except InvalidOperation:
                amount = None
                reasons.append("invalid amount")
            key = (row.get("client_ref", "").strip(), row.get("invoice_no", "").strip())
            if key in seen:
                reasons.append("duplicate client_ref + invoice_no")
            if key != ("", ""):
                seen.add(key)
            target = rejected if reasons else clean
            item = dict(row)
            if reasons:
                item["reject_reason"] = "; ".join(reasons)
                item["source_line"] = line_no
            else:
                item["amount"] = f"{amount:.2f}"
            target.append(item)
    output.mkdir(parents=True, exist_ok=True)
    def write(name, rows, fields):
        with (output / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
    write("cleaned_invoices.csv", clean, list(REQUIRED))
    write("rejected_rows.csv", rejected, [*REQUIRED, "source_line", "reject_reason"])
    report = {"input_rows": len(clean) + len(rejected), "accepted_rows": len(clean), "rejected_rows": len(rejected), "duplicate_keys": sum("duplicate" in row.get("reject_reason", "") for row in rejected)}
    (output / "quality_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw_invoices.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    print(json.dumps(process(args.input, args.output), indent=2))

if __name__ == "__main__":
    main()
